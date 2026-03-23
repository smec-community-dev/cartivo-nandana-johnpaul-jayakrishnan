from Core_app.models import Category

def category_list(request):
    return {
        "cat": Category.objects.all()
    }