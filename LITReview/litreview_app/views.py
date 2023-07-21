from itertools import chain
from operator import attrgetter
from urllib.parse import urlencode
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import CharField, Value, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Ticket, Review, UserFollows, RATING_CHAR_ON, RATING_CHAR_OFF, RATING_RANGE
from .forms import ReviewForm, TicketForm, UserFollowsForm
from django.views import View


class HomeView(View):
    def get(self, request):
        return redirect("flux") if request.user.is_authenticated else redirect("login")

class CreateTicketView(LoginRequiredMixin, View):
    def get(self, request, ticket_id=None):
        ticket_instance = Ticket.objects.get(pk=ticket_id) if ticket_id is not None else None
        form = TicketForm(instance=ticket_instance)
        context = {
            'form': form,
            'ticket_id': ticket_id
        }
        return render(request, 'review/create_ticket.html', context)

    def post(self, request, ticket_id=None):
        next_url = request.POST.get('next', '/')
        ticket_instance = Ticket.objects.get(pk=ticket_id) if ticket_id is not None else None
        form = TicketForm(request.POST, request.FILES, instance=ticket_instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user_id = request.user.id
            obj.save()
            return redirect(next_url)
        context = {
            'form': form,
            'ticket_id': ticket_id
        }
        return render(request, 'review/create_ticket.html', context)


class DeleteTicketView(LoginRequiredMixin, View):
    def get(self, request, ticket_id):
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.delete()
        return redirect('posts')

class EditTicketView(LoginRequiredMixin, View):
    """View to edit a ticket"""
    def get(self, request, ticket_id):
        ticket = Ticket.objects.get(id=ticket_id)
        form = TicketForm(instance=ticket)
        context = {'form': form, 'edit': True}
        return render(request, 'review/create_ticket.html', context)

    def post(self, request, ticket_id):
        ticket = Ticket.objects.get(id=ticket_id)
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if not form.is_valid():
            return HttpResponse(f"<p>{form.errors}</p>")
        form.save()
        return redirect('posts')


class CreateReviewView(LoginRequiredMixin, View):
    def get(self, request):
        review_form = ReviewForm()
        ticket_form = TicketForm()
        context = {'review_form': review_form,
                   'ticket_form': ticket_form
                   }
        return render(request, 'review/create_review.html', context)

    def post(self, request):
        user = request.user
        title = request.POST.get('title', False)
        description = request.POST.get('description', False)
        image = request.POST.get('image', False)
        ticket_form = TicketForm({'title': title,
                                  'description': description,
                                  'image': image,
                                  'user': user},
                                 request.FILES)
        if ticket_form.is_valid():
            ticket = ticket_form.save()
        else:
            return HttpResponse(f"<p>ticket_form errors : {ticket_form.errors}</p>")
        # review
        headline = request.POST.get('headline', False)
        body = request.POST.get('body', False)
        rating = request.POST.get('rating', False)
        review_form = ReviewForm({'headline': headline,
                                  'body': body,
                                  'rating': rating,
                                  'user': user,
                                  'ticket': ticket})
        if not review_form.is_valid():
            return HttpResponse(f"<p>review_form errors : {review_form.errors}</p>")
        review_form.save()
        return redirect('flux')

class CreateTicketAndReviewView(LoginRequiredMixin, View):
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

class EditReviewView(LoginRequiredMixin, View):
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
        user = request.user
        headline = request.POST.get('headline', False)
        body = request.POST.get('body', False)
        rating = request.POST.get('rating', False)
        review_form = ReviewForm({'headline': headline,
                                  'body': body,
                                  'rating': rating,
                                  'user': user,
                                  'ticket': ticket}, instance=review)
        if review_form.is_valid():
            review_form.save()
            return redirect('posts')
        else:
            return HttpResponse("<p>Form errors</p>")



class DeleteReviewView(LoginRequiredMixin, View):
    def get(self, request, review_id):
        review = Review.objects.get(id=review_id)
        review.delete()
        return redirect('posts')

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

class FollowersView(LoginRequiredMixin, View):
    def get(self, request):
        if request.method == "GET":
            follow_form = UserFollowsForm()
            users_followed = UserFollows.objects.filter(user=request.user)
            followed_by = UserFollows.objects.filter(
                followed_user=request.user)
            return render(
                request,
                "review/followers.html",
                {"follow_form": follow_form,
                 "users_followed": users_followed,
                 "followed_by": followed_by})

    def post(self, request):
        if request.method != "POST":
            return redirect("followers")
        form = UserFollowsForm(request.POST)
        oneself = request.user.username
        if form.is_valid() and (form.cleaned_data["followed_user"] != oneself):
            try:
                user_followed = User.objects.get(
                    username=form.cleaned_data["followed_user"])
                data = UserFollows(
                    user=request.user,
                    followed_user=user_followed)
                data.save()
                return redirect("flux")
            except Exception:
                return redirect("followers")
        else:
            return redirect("posts")


class DeleteUserFollowView( LoginRequiredMixin, View):
    ...


class FluxView(LoginRequiredMixin, View):
    template_name = "review/flux.html"

    def get(self, request):
        if request.user.is_authenticated:
            # Get objects:
            tickets = Ticket.objects.all()
            reviews = Review.objects.all()
            users = UserFollows.objects.all()
            # 1. Get all tickets from user
            ticket_user = tickets.filter(user=request.user)
            # 2. Get all tickets from followed_user-s
            ticket_followed_user = tickets.filter(
                user__id__in=users.filter(
                    user=request.user).values_list("followed_user_id")
            )

            all_tickets = ticket_user | ticket_followed_user
            # 1. Get all reviews from user
            review_user = reviews.filter(user=request.user)
            # 2. Get all reviews from followed_user-s
            review_followed_user = reviews.filter(
                user__id__in=users.filter(
                    user=request.user).values_list("followed_user_id")
            )
            # 3. Get reviews from un-followed_user-s that review the user's ticket
            review_unfollowed_reviewed = reviews.filter(
                ticket__id__in=tickets.filter(
                    user=request.user).values_list("id")
            )

            all_reviews = (
                    review_user | review_followed_user | review_unfollowed_reviewed
            )
            # Sort all posts by -time_created:
            flux_posts = list(
                sorted(chain(all_tickets, all_reviews),
                       key=attrgetter("time_created"),
                       reverse=True)
            )
            return render(
                request,
                self.template_name,
                context={"data": flux_posts, "range_5": range(5)}
            )
        else:
            return redirect("login")


class DeleteContentView(View):
    """Delete the content (ticket or review) identified by its id."""

    def get_redirect_url(self, content):
        if content == "ticket":
            return "posts"
        return "posts" if content == "review" else "flux"

    def get(self, request, content, id_delete):
        try:
            if content == "ticket":
                Ticket.objects.get(Q(id=id_delete) & Q(user=request.user)).delete()
            elif content == "review":
                Review.objects.get(Q(id=id_delete) & Q(user=request.user)).delete()
        except Ticket.DoesNotExist:
            pass
        except Review.DoesNotExist:
            pass
        return redirect(self.get_redirect_url(content))