from itertools import chain
from operator import attrgetter

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import CharField, Value, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from .models import Ticket, Review, UserFollows, RATING_CHAR_ON, RATING_CHAR_OFF, RATING_RANGE
from .forms import ReviewForm, TicketForm, UserFollowsForm
from django.views import View


class HomeView(View):
    def get(self, request):
        return redirect("flux") if request.user.is_authenticated else redirect("login")

class CreateTicketView(LoginRequiredMixin, View):
    template_name = 'review/create_ticket.html'
    def get(self, request, ticket_id=None):
        ticket_instance = Ticket.objects.get(pk=ticket_id) if ticket_id is not None else None
        form = TicketForm(instance=ticket_instance)
        context = {
            'form': form,
            'ticket_id': ticket_id
        }
        return render(request, self.template_name, context)

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
        return render(request, self.template_name , context)

class EditTicketView(LoginRequiredMixin, View):
    template_name = 'review/edit_review.html'

    def get(self, request, ticket_id):
        instanced_ticket = Ticket.objects.get(pk=ticket_id)
        form = TicketForm(instance=instanced_ticket)
        infos = {'page_title': 'Ticket', 'form': form, 'instanced_ticket': instanced_ticket}
        return render(request, self.template_name, infos)

    def post(self, request, ticket_id):
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            data_ticket = Ticket.objects.get(pk=ticket_id)
            data_ticket.title = form.cleaned_data['title']
            data_ticket.description = form.cleaned_data['description']
            if form.cleaned_data['image']:
                data_ticket.image = form.cleaned_data['image']
            data_ticket.save()
        return redirect('flux')


class DeleteTicketView(LoginRequiredMixin, DeleteView):
    model = Ticket
    success_url = reverse_lazy('flux')
    template_name = 'review/delete_ticket.html'



class CreateReviewView(LoginRequiredMixin, View):
    template_name = 'review/create_review.html'

    def get(self, request, ticket_id=None):
        instanced_ticket = get_object_or_404(Ticket, pk=ticket_id) if ticket_id else None
        ticket_form = TicketForm()
        review_form = ReviewForm()
        context = {
            'page_title': 'Review',
            'instanced_ticket': instanced_ticket,
            'ticket_form': ticket_form,
            'review_form': review_form,
            'range': range(6),
        }
        return render(request, self.template_name, context)

    def post(self, request, ticket_id=None):
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            if ticket_id:
                review.ticket = get_object_or_404(Ticket, pk=ticket_id)
            review.save()
            return redirect('flux')
        else:
            ticket_form = TicketForm()
            context = {
                'page_title': 'Review',
                'ticket_form': ticket_form,
                'review_form': review_form,
                'range': range(6),
            }
            return render(request, self.template_name, context)

class EditReviewView(LoginRequiredMixin, View):
    template_name = 'review/edit_ticket.html'

    def get(self, request, review_id):
        instanced_review = Review.objects.get(pk=review_id)
        form = ReviewForm(instance=instanced_review)
        infos = {'page_title': 'Review', 'form': form, 'range': range(6), 'instanced_review': instanced_review}
        return render(request, self.template_name, infos)

    def post(self, request, review_id):
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            data_review = Review.objects.get(pk=review_id)
            data_review.headline = form.cleaned_data['headline']
            data_review.body = form.cleaned_data['body']
            data_review.rating = form.cleaned_data['rating']
            data_review.save()
            return redirect('flux')
        else:
            return render(request, self.template_name, {'form': form, 'range': range(6)})


class DeleteReviewView(LoginRequiredMixin, DeleteView):
    model = Review
    success_url = reverse_lazy('flux')

class PostsView(LoginRequiredMixin ,View):
    template_name = 'review/posts.html'

    def get(self, request):
        user = request.user
        if user.is_active:
            tickets = Ticket.objects.all()
            reviews = Review.objects.all()
            tickets_list = []
            for ticket_data in tickets:
                for review_data in reviews:
                    if ticket_data.id == review_data.ticket_id:
                        tickets_list.append(ticket_data)
            data_ticket = Ticket.objects.filter(user=user)
            data_review = Review.objects.filter(user=user)
            infos = {'page_title': 'Posts Personnels', 'data_ticket': data_ticket, 'data_review': data_review,
                     'tickets_list': tickets_list}
            return render(request, self.template_name, infos)
        else:
            return redirect('login')
class FollowersView(LoginRequiredMixin, View):
    def get(self, request):
        # This method handles GET requests for the subscriptions page
        title = "Abonnements"
        users = User.objects.all()
        user_follows = UserFollows.objects.all()
        user = request.user
        subscribers = user.followed_by.all()
        form = UserFollowsForm()

        return render(request, 'review/followers.html', {
            'title': title,
            'form': form,
            'current_user': users,
            'subscribers': subscribers,
            'user_follows': user_follows
        })

    def post(self, request):
        # This method handles POST requests when the user submits the form to follow another user
        title = "Abonnements"
        users = User.objects.all()
        user = request.user
        subscribers = user.followed_by.all()

        try:
            entry = request.POST['followed_user']
            user_to_follow = User.objects.get(username=entry)
            if user_to_follow == user:
                raise ValueError()
            for u in users:
                if u.username == entry:
                    # Create a new UserFollows object to indicate that the current user follows the specified user
                    UserFollows.objects.create(user=request.user, followed_user=user_to_follow)
        except ValueError:
            form = UserFollowsForm(request.POST)
            messages.error(request, 'Vous ne pouvez pas vous suivre')
        except Exception:
            form = UserFollowsForm(request.POST)
            messages.error(request, "Cet utilisateur n'est pas répertorié")
        else:
            # If the user is successfully followed, display a success message and redirect back to the subscriptions page
            messages.success(request, "Utilisateur suivi !")
            return redirect("followers")

        form =UserFollowsForm()
        user_follows = UserFollows.objects.all()

        return render(request, 'review/followers.html', {
            'title': title,
            'form': form,
            'current_user': user,
            'subscribers': subscribers,
            'user_follows': user_follows
        })


class DeleteUserFollowView(LoginRequiredMixin, DeleteView, SuccessMessageMixin):
    model = UserFollows
    success_url = reverse_lazy('followers')
    success_message = "Abonnement résilié"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = User.objects.get(id=self.request.user.id)
        context['followed_user'] = UserFollows.objects.exclude(
            user=current_user)
        return context

class FluxView(LoginRequiredMixin, View):
    template_name = 'review/flux.html'

    def get(self, request):
        """Show user's feed"""
        tickets = Ticket.objects.all()
        reviews = Review.objects.all()
        context = {"tickets": tickets,
                   "reviews": reviews}
        return render(request, self.template_name, context )


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