from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. የአድሚን ገጽ
    path('admin/', admin.site.urls),
    
    # 2. የጃንጎ የራሱ የሎግአውት እና ሎግኢን ሲስተም (ስህተቱን የሚያስተካክለው ይሄ ነው)
    path('accounts/', include('django.contrib.auth.urls')), 
    
    # 3. ያንተ አፕ (Products)
    path('', include('products.urls')),
]

# 4. ምስሎች (Images) በብራውዘር ላይ እንዲታዩ የሚያደርግ
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)