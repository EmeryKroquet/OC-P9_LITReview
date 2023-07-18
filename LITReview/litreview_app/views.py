from itertools import chain
from urllib.parse import urlencode
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import CharField, Value
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from .models import Ticket, Review, UserFollows, RATING_CHAR_ON, RATING_CHAR_OFF, RATING_RANGE
from .forms import ReviewForm, TicketForm, UserFollowsForm
from django.views import View


class HomeView(View):
    def get(self, request):
        return render(request, 'review/home.html')
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
    def get(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        ticket()
        return redirect('posts')

class EditTicketView(LoginRequiredMixin, View):
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


class PostsView(LoginRequiredMixin, View):
    template_name = 'review/posts.html'

    def get(self, request):
        user = request.user
        ticket = Ticket.objects.filter(user=user)
        ticket = ticket.annotate(content_type=Value('TICKET', CharField()))

        ticket_not_reviewed = ticket.exclude(id__in=[review.ticket.id for review in Review.objects.filter(
            ticket__in=ticket)]).annotate(ticket_status=Value('not_reviewed', CharField()))
        ticket_reviewed = ticket.filter(
            id__in=[review.ticket.id for review in Review.objects.filter(ticket__in=ticket)]).annotate(
            ticket_status=Value('already_reviewed', CharField()))

        review = Review.objects.filter(user=user)
        review = review.annotate(content_type=Value('REVIEW', CharField()))

        posts = chain(ticket_not_reviewed, ticket_reviewed, review)
        context = {'posts': posts,
                   'rating_range': RATING_RANGE,
                   'rating_char_on': RATING_CHAR_ON,
                   'rating_char_off': RATING_CHAR_OFF}
        return render(request, self.template_name, context)

_MESSAGES = {
    'unknown_user': "Utilisateur inconnu !",
    'do_not_follow_yourself': "Veuillez renseigner un nom d'utilisateur autre que le votre.",
    'subscription_success': "Vous suivez désormais l'utilisateur {username} !",
    'already_following': "Vous suivez déjà l'utilisateur {username} !",
    'stopped_subscription': "Vous ne suivez désormais plus l'utilisateur {username}"

}
class FollowersView(LoginRequiredMixin, View):
    def get(self, request):
        follows_form = UserFollowsForm()
        user = User.objects.get(username=request.user.username)
        user_subscriptions = list(UserFollows.objects.filter(user=user))
        subscribers = [user_follow.user for user_follow in UserFollows.objects.filter(followed_user=user)]

        error_message = request.GET.get('error_message') if request.GET.get('error_message') != 'None' else None
        validated_message = request.GET.get('validated_message') if request.GET.get(
            'validated_message') != 'None' else None
        followed_user = request.GET.get('followed_user') if request.GET.get('followed_user') != 'None' else None
        if error_message is not None:
            error_message = _MESSAGES[error_message].format(username=followed_user)
        else:
            error_message = None
        if validated_message is not None:
            validated_message[validated_message].format(username=followed_user)
        else:
            validated_message = None
            context = {'follows_form': follows_form,
                       'subscriptions': user_subscriptions,
                       'subscribers': subscribers,
                       'error_message': error_message,
                       'validated_message': validated_message}
            return render(request, 'review/followers.html', context)

    def post(self, request):
        error_message = None
        validated_message = None
        user = request.user
        user_followed_username = request.POST.get('followed_user', False)
        if not User.objects.filter(username=user_followed_username).exists():
            error_message = 'unknown_user'
        elif user_followed_username == user.username:
            error_message = 'do_not_follow_yourself'
        else:
            followed_user_id = User.objects.get(username=user_followed_username).id
            follows_form = UserFollowsForm({'user': user,
                                           'followed_user': followed_user_id})
            if follows_form.is_valid():
                follows_form.save()
                validated_message = 'subscription_success'
            else:
                error_message = 'already_following'
        query = {'error_message': error_message,
                 'validated_message': validated_message,
                 'followed_user': user_followed_username}
        query_string = urlencode(query)
        return redirect(f'/followers/?{query_string}')

class DeleteUserFollowView( LoginRequiredMixin, View):
    def get(self, request, followed_user_id):
        user = request.user
        followed_user = User.objects.get(id=followed_user_id)
        subscription_to_delete = UserFollows.objects.get(user=user, followed_user=followed_user)
        subscription_to_delete.delete()
        validated_message = 'stopped_subscription'
        query = {'validated_message': validated_message,
                     'followed_user': followed_user.username}
        query_string = urlencode(query)
        return redirect(f'/followers/?{query_string}')


    def post(self, request):
        user = request.user
        follower_username = request.POST.get('followed_user')

        if not User.objects.filter(username=follower_username).exists():
            error_message = 'unknown_user'
        elif follower_username == user.username:
            error_message = 'do_not_follow_yourself'
        else:
            follower_user_id = User.objects.get(username=follower_username).id
            follows_form = UserFollowsForm({'user': user, 'followed_user': follower_user_id})
            if follows_form.is_valid():
                follows_form.save()
                validated_message = 'subscription_success'
            else:
                error_message = 'already_following'

        query = {
            'error_message': error_message,
            'validated_message': validated_message,
                 'followed_user': follower_username
                 }
        query_string = urlencode(query)

        return redirect(f'followers?{query_string}')


class DeleteFollowers(LoginRequiredMixin, View):
    def get(self, request, followed_user_id):
        user = request.user
        followed_user = get_object_or_404(User, id=followed_user_id)
        subscription_to_delete = get_object_or_404(UserFollows, user=user, followed_user=followed_user)
        subscription_to_delete.delete()
        validated_message = 'stopped_subscription'

        query = {'validation_message': validated_message, 'followed_user': followed_user.username}
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

