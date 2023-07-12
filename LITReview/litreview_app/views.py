from itertools import chain
from urllib.parse import urlencode

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import CharField, Value
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator

from .models import Ticket, Review, UserFollows
from .forms import ReviewForm, TicketForm, UserFollowsForm
from django.views import View


class HomeView(LoginRequiredMixin, View):
    template_name = "'users:login'"
    def get(self, request):
        return redirect("flux")
class CreateTicketView(LoginRequiredMixin, View):
    def get(self, request):
        form = TicketForm()
        return render(request, "review/create_ticket.html", {"form": form})

    def post(self, request):
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect("posts")
        return redirect("flux")

class DeleteTicketView(LoginRequiredMixin, View):
    template_name = "users:login"
    def get(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        ticket()
        return redirect('posts')

class EditTicketView(LoginRequiredMixin, View):
    template_name = "users:login"
    """View to edit a ticket"""
    def get(self, request, ticket_id):
        ticket = Ticket.objects.get(id=ticket_id)
        form = TicketForm(instance=ticket)
        context = {'form': form,
                   'edit': True}
        return render(request, 'ticket/create_ticket.html', context)


    def post(self, request, ticket_id):
        ticket = Ticket.objects.get(id=ticket_id)
        actual_user = request.user
        title = request.POST.get('title', False)
        description = request.POST.get('description', False)
        image = request.POST.get('image', False)
        form = TicketForm({'title': title,
                           'description': description,
                           'image': image,
                           'user': actual_user,
                           'id': id},
                          request.FILES, instance=ticket)
        if not form.is_valid():
            return HttpResponse(f"<p>{form.errors}</p>")
        form.save()
        return redirect('/posts/')

@method_decorator(login_required, name='dispatch')
class CreateReviewView(View):
    def get(self, request):
        review_form = ReviewForm()
        ticket_form = TicketForm()
        context = {'review_form': review_form,
                   'ticket_form': ticket_form
                   }
        return render(request, 'review/create_review.html', context)

    def post(self, request):
        actual_user = request.user

        # Create ticket
        ticket_form = TicketForm(request.POST, request.FILES)
        if not ticket_form.is_valid():
            return HttpResponse(f"<p>ticket_form errors: {ticket_form.errors}</p>")

        ticket = ticket_form.save(commit=False)
        ticket.user = actual_user
        ticket.save()
        # Create review
        review_form = ReviewForm(request.POST)
        if not review_form.is_valid():
            return HttpResponse(f"<p>review_form errors: {review_form.errors}</p>")
        review = review_form.save(commit=False)
        review.user = actual_user
        review.ticket = ticket
        review.save()
        return redirect('flux')


@method_decorator(login_required, name='dispatch')
class EditReviewView(View):
    def get(self, request, review_id):
        review = Review.objects.get(id=review_id)
        review_form = ReviewForm(instance=review)
        ticket = review.ticket
        context = {
            'review_form': review_form,
            'ticket': ticket,
            'edit': True
        }
        return render(request, 'review/create_review_and_ticket.html', context)

    def post(self, request, review_id):
        review = Review.objects.get(id=review_id)
        ticket = Ticket.objects.get(id=review.ticket.id)
        current_user = request.user
        review_form = ReviewForm()
        context = {ticket: 'ticket',
                   current_user: 'current_user'}
        if review_form.is_valid():
            review_form.save()
            return redirect('posts', context)
        else:
            return HttpResponse("<p>Form errors</p>")


@method_decorator(login_required, name='dispatch')
class DeleteReviewView(View):
    def get(self, request, review_id):
        review = Review.objects.get(id=review_id)
        review.delete()
        return redirect('posts')

#@method_decorator(login_required, name='dispatch')
class TicketAndReviewView(LoginRequiredMixin, View):
    template_name = 'users:login.html'
    def get(self, request, ticket_id):
        review_form = ReviewForm()
        ticket = Ticket.objects.get(id=ticket_id)
        context = {'review_form': review_form,
                   'ticket': ticket
                   }
        return render(request, 'review/create_review_and_ticket.html', context)

    def post(self, request, ticket_id):
        # ticket
        ticket = Ticket.objects.get(id=ticket_id)
        # review
        current_user = request.user
        headline = request.POST.get('headline', False)
        body = request.POST.get('body', False)
        rating = request.POST.get('rating', False)
        review_form = ReviewForm()
        context = {'headline': headline,
                                  'body': body,
                                  'rating': rating,
                                  'user': current_user,
                                  'ticket': ticket
                   }
        if not review_form.is_valid():
            return HttpResponse(f"<p>review_form errors : {review_form.errors}</p>", context)
        review_form.save()
        return redirect('flux')


RATING_RANGE = range(1, 6)
RATING_CHAR_ON = "★"
RATING_CHAR_OFF = "☆"
class PostsView(LoginRequiredMixin, View):
    template_name = 'users:login.html'
    def get(self, request):
        current_user = request.user
        # Fetch own tickets and annotate content type
        my_tickets = Ticket.objects.filter(user=current_user).annotate(content_type=Value('TICKET', CharField()))
        # Fetch own tickets not reviewed
        my_tickets_not_reviewed = my_tickets.exclude(
            id__in=Review.objects.filter(ticket__in=my_tickets).values_list('ticket__id')).annotate(
            ticket_status=Value('not_reviewed', CharField()))
        # Fetch own tickets already reviewed
        my_tickets_reviewed = my_tickets.filter(
            id__in=Review.objects.filter(ticket__in=my_tickets).values_list('ticket__id')).annotate(
            ticket_status=Value('already_reviewed', CharField()))
        # Fetch own reviews and annotate content type
        my_reviews = Review.objects.filter(user=current_user).annotate(content_type=Value('REVIEW', CharField()))
        # Combine tickets not reviewed, tickets reviewed, and reviews
        posts = chain(my_tickets_not_reviewed, my_tickets_reviewed, my_reviews)
        return render(request, 'review/posts.html', context={'posts': posts,
                                                            'rating_range': RATING_RANGE,
                                                            'rating_char_on': RATING_CHAR_ON,
                                                            'rating_char_off': RATING_CHAR_OFF})
@method_decorator(login_required, name='dispatch')
class FollowersView(View):
    template_name = 'review/followers.html'

    def get(self, request):
        nav_bar = 'followers'
        user = request.user
        user_follows = UserFollows.objects.filter(followed_user=user.id)
        following = UserFollows.objects.filter(user=user.id)
        user_follow = UserFollows()
        found_user = ""

        form = UserFollowsForm()
        user_follows = UserFollows.objects.filter(user=user)
        already_followed = [pair.followed_user.id for pair in user_follows]
        options = User.objects.all().exclude(
            id__in=already_followed).exclude(id=user.id)

        result_list = list(chain(options, already_followed))
        form.fields['followed_user'].queryset = options
        return render(request, self.template_name, locals())

    def post(self, request):
        user = request.user
        user_follows = UserFollows.objects.filter(user=user)
        already_followed = [pair.followed_user.id for pair in user_follows]
        searched_value = request.GET.get('searched', None)
        try:
            found_user = User.objects.get(username__iexact=searched_value)
            user_follow_instance = UserFollows(user=user, followed_user=found_user)
            if user != found_user:
                user_follow_instance.save()
            else:
               error_message = "vous ne pouvez pas vous suivre!"
        except User.DoesNotExist:
            found_user = None
        except IntegrityError:
            found_user = None
            error_message = "Vous êtes déjà abonner à cet utilisateur"
        return render(request, self.template_name, locals())

@method_decorator(login_required, name='dispatch')
class DeleteUserFollowView(View):
    def get(self, request, user_follow_id):
        user_follows = get_object_or_404(UserFollows, pk=user_follow_id)
        user_follows.delete()
        return redirect('followers')


    def post(self, request):
        current_user = request.user
        follower_username = request.POST.get('followed_user')

        if not User.objects.filter(username=follower_username).exists():
            error_message = 'unknown_user'
        elif follower_username == current_user.username:
            error_message = 'do_not_follow_yourself'
        else:
            follower_user_id = User.objects.get(username=follower_username).id
            follows_form = UserFollowsForm({'user': current_user, 'followed_user': follower_user_id})
            if follows_form.is_valid():
                follows_form.save()
                validation_message = 'subscription_success'
            else:
                error_message = 'already_following'

        query = {'error_message': error_message, 'validation_message': validation_message,
                 'followed_user': follower_username
                 }
        query_string = urlencode(query)

        return redirect(f'followers?{query_string}')


class DeleteFollowers(LoginRequiredMixin, View):
    template_name = 'users:login.html'
    """Link to delete subscription"""
    def get(self, request, followed_user_id):
        actual_user = request.user
        followed_user = get_object_or_404(User, id=followed_user_id)
        subscription_to_delete = get_object_or_404(UserFollows, user=actual_user, followed_user=followed_user)
        subscription_to_delete.delete()
        validation_message = 'stopped_subscription'

        query = {'validation_message': validation_message, 'followed_user': followed_user.username}
        query_string = urlencode(query)

        return redirect(f'followers?{query_string}')



class FluxView(LoginRequiredMixin, View):
    template_name = 'users:login.html'
    def get(self, request):
        user = request.user
        followed_users_ids = self.get_followed_users_ids(user)
        reviews = self.get_users_reviews(user, followed_users_ids)
        tickets = self.get_users_tickets(user, followed_users_ids)
        user_reviews = Review.objects.filter(user_id=user.id)
        tickets_reviewed_by_user = self.get_tickets_and_reviewed_by_user(user_reviews)

        posts = sorted(
            list(chain(tickets, reviews)),
            key=lambda post: post.time_created,
            reverse=True
        )

        return render(request, 'review/flux.html',
                      {'nav_bar': 'flux',
                       'posts': posts,
                       'tickets': tickets,
                       'reviews': reviews,
                       'tickets_reviewed_by_user': tickets_reviewed_by_user})

    @staticmethod
    def get_followed_users_ids(user):
        return UserFollows.objects.filter(user=user).values_list('followed_user_id', flat=True)

    @staticmethod
    def get_users_reviews(user, followed_users_ids):
        reviews = Review.objects.filter(user_id__in=list(chain([user.id], followed_users_ids)))
        for review in reviews:
            review.type = 'REVIEW'
        return reviews

    @staticmethod
    def get_users_tickets(user, followed_users_ids):
        tickets = Ticket.objects.filter(user_id__in=list(chain([user.id], followed_users_ids)))
        for ticket in tickets:
            ticket.type = 'TICKET'
            ticket.display = 'NORMAL'
        return tickets

    @staticmethod
    def get_tickets_and_reviewed_by_user(user_reviews):
        return Ticket.objects.filter(review__in=user_reviews)

