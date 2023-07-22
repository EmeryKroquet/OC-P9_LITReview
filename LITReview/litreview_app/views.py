from itertools import chain
from operator import attrgetter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import CharField, Value, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
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

class CreateReviewView(View):
    def get(self, request, id_ticket=None):
        if id_ticket:
            ticket = get_object_or_404(Ticket, id=id_ticket)
            form = ReviewForm()
            context = {"form": form,
                       "ticket": ticket
                       }
            return render(request, "review/create_review.html", context)
        else:
            ticket = TicketForm()
            form = ReviewForm()
            context = {"form": form,
                       "ticket": ticket
                       }
            return render(request, "review/create_review.html", context)

    def post(self, request, id_ticket=None):
        if id_ticket:
            ticket = get_object_or_404(Ticket, id=id_ticket)
            form = ReviewForm(request.POST)
            if not form.is_valid():
                return redirect(f"/create_review/{id_ticket}/")
            ticket = ticket
            headline = form.cleaned_data["headline"]
            rating = form.cleaned_data["rating"]
            body = form.cleaned_data["body"]
            user = request.user
            data = Review(ticket=ticket, headline=headline, user=user, rating=rating, body=body)
            data.save()
        else:
            ticket_form = TicketForm(request.POST, request.FILES)
            review_form = ReviewForm(request.POST)
            if not ticket_form.is_valid() or not review_form.is_valid():
                return redirect("flux")
            title = ticket_form.cleaned_data["title"]
            description = ticket_form.cleaned_data["description"]
            try:
                image = request.FILES["image"]
            except KeyError:
                image = None
            user = request.user
            data_ticket = Ticket(title=title, description=description, image=image, user=user)
            data_ticket.save()

            ticket = data_ticket
            headline = review_form.cleaned_data["headline"]
            rating = review_form.cleaned_data["rating"]
            body = review_form.cleaned_data["body"]
            user = request.user
            data_review = Review(ticket=ticket, headline=headline, user=user, rating=rating, body=body)
            data_review.save()

        return redirect("/posts/")


def _extracted_from_post_6(id_modify, request, form):
    ticket = Ticket.objects.get(Q(id=id_modify) & Q(user=request.user))
    ticket.title = form.cleaned_data["title"]
    ticket.description = form.cleaned_data["description"]

    if request.FILES:
        ticket.image = request.FILES["image"]
    ticket.save()

    # Optionnal
    Review.objects.filter(ticket__id__in=Ticket.objects.filter(id=id_modify).values_list("id")).delete()


class ModifyContentView(LoginRequiredMixin, View):
    """Allow user to modify their own tickets and reviews."""

    def get(self, request, content, id_modify):
        try:
            if content == "ticket":
                ticket = Ticket.objects.get(Q(id=id_modify) & Q(user=request.user))
                form = TicketForm(instance=ticket, initial={
                    'title': ticket.title,
                    'description': ticket.description,
                })
                return render(request, 'review/modify_content.html', {"form": form, "old_image": ticket.image})

            elif content == "review":
                review = Review.objects.get(Q(id=id_modify) & Q(user=request.user))
                form = ReviewForm(instance=review, initial={
                    'headline': review.headline,
                    'rating': review.rating,
                    'body': review.body,
                })
                return render(request, 'review/modify_content.html', {"form": form, "ticket": review.ticket})

        except Ticket.DoesNotExist:
            return redirect("/flux/")
        except Review.DoesNotExist:
            return redirect("/flux/")

    def post(self, request, content, id_modify):
        try:
            if content == "ticket":
                form = TicketForm(request.POST, request.FILES)
                if form.is_valid():
                    _extracted_from_post_6(id_modify, request, form)
                return redirect("/posts/")

            elif content == "review":
                form = ReviewForm(request.POST)
                if form.is_valid():
                    review = Review.objects.get(Q(id=id_modify) & Q(user=request.user))
                    review.headline = form.cleaned_data["headline"]
                    review.rating = form.cleaned_data["rating"]
                    review.body = form.cleaned_data["body"]
                    review.save()

                return redirect("posts")

        except Ticket.DoesNotExist:
            return redirect("/flux/")
        except Review.DoesNotExist:
            return redirect("/flux/")

    # TODO Rename this here and in `post`


RATING_RANGE = range(1, 6)
RATING_CHAR_ON = '★'
RATING_CHAR_OFF = '☆'

class PostsView(LoginRequiredMixin ,View):
    def get(self, request):
        own_tickets = Ticket.objects.filter(user=request.user)
        own_reviews = Review.objects.filter(user=request.user)
        own_data = sorted(
            chain(own_tickets, own_reviews),
            key=attrgetter("time_created"), reverse=True)
        ticket_not_reviewed = own_tickets.exclude(id__in=[review.ticket.id for review in Review.objects.filter(
            ticket__in=own_tickets)]).annotate(ticket_status=Value('not_reviewed', CharField()))
        ticket_reviewed = own_tickets.filter(
            id__in=[review.ticket.id for review in Review.objects.filter(ticket__in=own_tickets)]).annotate(
            ticket_status=Value('already_reviewed', CharField()))
        posts = chain(ticket_not_reviewed, ticket_reviewed, own_reviews)
        context = {'posts': posts,
                   'rating_range': RATING_RANGE,
                   'rating_char_on': RATING_CHAR_ON,
                   'rating_char_off': RATING_CHAR_OFF,
                   "data": own_data,
                   "range": range(5)
                   }
        return render(request, "review/posts.html", context)
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
        user = request.user.username
        if form.is_valid() and (form.cleaned_data["followed_user"] != user):
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
    def get(self, request, id_delete):
        try:
            UserFollows.objects.get(Q(id=id_delete) & Q(user=request.user)).delete()
            return redirect("followers")
        except UserFollows.DoesNotExist:
            return redirect("followers")


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


class DeleteContentView(LoginRequiredMixin, View):
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