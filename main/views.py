from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

def home(request):
    recipes = Recipe.objects.all()
    query = request.GET.get('q')

    if query:
        recipes = recipes.filter(
            title__icontains=query
        )
    return render(request, 'home.html', {'recipes': recipes})

@login_required
@permission_required('recipes.add_recipe', raise_exception=True)
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            return redirect('home')
    else:
        form = RecipeForm()
    return render(request, 'add_recipe.html', {'form': form})

@login_required
@permission_required('recipes.change_recipe', raise_exception=True)
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user != recipe.author:
        return redirect('home')

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'edit_recipe.html', {'form': form})

@login_required
@permission_required('recipes.delete_recipe', raise_exception=True)
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user != recipe.author:
        return redirect('home')

    if request.method == 'POST':
        recipe.delete()
        return redirect('home')

    return render(request, 'delete_recipe.html', {'recipe': recipe})

@login_required
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    comments = recipe.comments.all().order_by('-created_at')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect('login')

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = recipe
            comment.user = request.user
            comment.save()
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        form = CommentForm()

    return render(request, 'recipe_detail.html', {
        'recipe': recipe,
        'comments': comments,
        'form': form
    })

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'profile.html', {'form': form})

