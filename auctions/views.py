from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max, OuterRef, F, Subquery
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import User, AuctionListings, WatchList, Bids, Comments


def index(request):
    listings = AuctionListings.objects.all()
    highest_bid_subquery = Bids.objects.filter(listing = OuterRef('pk')).order_by('-amount')
    listing_with_highest_bid = listings.annotate(highest_bid = Subquery(highest_bid_subquery.values('amount')[:1]))

    return render(request, "auctions/index.html", {
        "listings": listing_with_highest_bid,
        "header": "Active Listings" 
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method == 'GET':
        return render(request, 'auctions/create.html')
    else:
        title = request.POST["title"]
        content = request.POST["content"]
        starting_price = request.POST["starting_price"]
        category = request.POST["category"]
        image = request.FILES["image"]
        
        new_listing = AuctionListings(title=title, description=content, starting_price=starting_price, category=category, image=image, creator=request.user)

        new_listing.save()

        return HttpResponseRedirect(reverse("index"))
    
def listing(request, listing_id):
    listing = get_object_or_404(AuctionListings, id=listing_id)
    is_creator = listing.creator == request.user if request.user.is_authenticated else False
    watchlist_entry= None
    if request.user.is_authenticated:
        watchlist_entry = WatchList.objects.filter(user_id = request.user, auction_id = listing).first()
    highest_bid = Bids.objects.filter(listing = listing).aggregate(Max('amount'))['amount__max']
    highest_bid_user = None

    if highest_bid is not None:
        highest_bid_entry = Bids.objects.filter(listing=listing, amount = highest_bid).first()
        highest_bid_user = highest_bid_entry.user
    
    context = {"listing":listing, "highest_bid":highest_bid, "highest_bid_user":highest_bid_user}
    context["is_creator"] = is_creator
    if watchlist_entry:
        context["watchlist_entry"] = watchlist_entry

    comments = Comments.objects.filter(listing = listing).all()
    if comments:
        context["comments"] = comments


    if request.method =='GET':
        return render(request, 'auctions/listing.html', context)
    else:
        is_close_listing = False
        new_bid = request.POST.get('bid')
        if request.POST.get('form_name') == 'close_listing_form':
            is_close_listing = request.POST.get('close_listing')
        new_comment = request.POST.get('comment')
        print(f'new bid: {new_bid}, is_close_listing: {is_close_listing}, new_comment: {new_comment}')
        if new_bid:
            new_bid = int(new_bid)
            if highest_bid is not None:
                if new_bid > highest_bid:
                    bid = Bids(user = request.user, listing = listing, amount = new_bid)
                    bid.save()
                    return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
                else:
                    return HttpResponse("Amount entered is smaller than current price, please enter a valid amount")
            else:
                bid = Bids(user = request.user, listing = listing, amount = new_bid)
                bid.save() 
                return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
        elif is_close_listing:
            listing.is_open = False
            listing.save()
            return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
        elif new_comment:
            comment = Comments(user= request.user, listing = listing, content= new_comment)
            comment.save()
            return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
        else:
            user_add = request.POST.get('user-add')
            user_remove = request.POST.get('user-remove')
            print(user_add, user_remove)
            if user_add:
                new_watchlist = WatchList(user = request.user, auction = listing)
                new_watchlist.save()
            elif user_remove:
                watchlist = WatchList.objects.filter(user = request.user, auction = listing).first()
                watchlist.delete()
            return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
        
def watchlist(request, user_id):
    watchlist = WatchList.objects.filter(user=request.user).all()
    highest_bid_subquery = Bids.objects.filter(listing = OuterRef('auction')).order_by('-amount')
    watchlist_with_highest_bid = watchlist.annotate(highest_bid = Subquery(highest_bid_subquery.values('amount')[:1]))

    if request.method == 'GET':
        return render(request, 'auctions/watchlist.html', {
            "watchlist":watchlist_with_highest_bid
        })
    else:
        auction = request.POST.get('remove')
        listing = WatchList.objects.filter(user = request.user, auction = auction).first()
        listing.delete()
        return HttpResponseRedirect(reverse('watchlist', args=(user_id,)))

def categories(request):
    categories = AuctionListings.objects.filter(is_open=True).values_list('category', flat=True).distinct()
    return render(request, 'auctions/categories.html', {
        "categories":categories
    })

def category(request, category):
    listings = AuctionListings.objects.filter(category=category, is_open=True).all()
    return render(request, 'auctions/category.html', {
        "listings":listings,
        "category":category,
        "header": "Active Listings"
    })
    