"""
Wishlist Serializers for VynilArt API
Note: This project uses GraphQL only, but serializers are kept for compatibility
"""
from rest_framework import serializers
from api.models.wishlist import Wishlist, WishlistSettings


class WishlistSettingsSerializer(serializers.ModelSerializer):
    """Wishlist settings serializer"""
    class Meta:
        model = WishlistSettings
        fields = [
            'id', 'user', 'auto_add', 'max_items',
            'notification_preferences', 'privacy_settings',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WishlistSerializer(serializers.ModelSerializer):
    """Wishlist serializer"""
    product_name = serializers.CharField(source='product.name_ar', read_only=True)
    product_image = serializers.CharField(source='product.main_image', read_only=True)
    product_price = serializers.DecimalField(
        source='product.base_price', read_only=True, max_digits=10, decimal_places=2
    )
    product_stock = serializers.IntegerField(
        source='product.stock', read_only=True
    )
    is_available = serializers.SerializerMethodField()
    days_in_wishlist = serializers.SerializerMethodField()
    
    class Meta:
        model = Wishlist
        fields = [
            'id', 'user', 'product', 'product_name', 'product_image',
            'product_price', 'product_stock', 'priority',
            'notification_preferences', 'notes', 'is_public',
            'is_active', 'created_at', 'updated_at',
            'is_available', 'days_in_wishlist'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_available(self, obj):
        """Check if product is available"""
        return obj.product.is_active and obj.product.stock > 0
    
    def get_days_in_wishlist(self, obj):
        """Calculate days in wishlist"""
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        return delta.days


class WishlistCreateSerializer(serializers.ModelSerializer):
    """Wishlist creation serializer"""
    class Meta:
        model = Wishlist
        fields = [
            'product', 'priority', 'notification_preferences',
            'notes', 'is_public', 'is_active'
        ]
    
    def validate(self, data):
        """Validate unique constraint"""
        user = self.context['request'].user
        product = data.get('product')
        
        if Wishlist.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError(
                "This product is already in your wishlist"
            )
        return data
    
    def create(self, validated_data):
        """Create wishlist item"""
        user = self.context['request'].user
        return Wishlist.objects.create(user=user, **validated_data)


class WishlistUpdateSerializer(serializers.ModelSerializer):
    """Wishlist update serializer"""
    class Meta:
        model = Wishlist
        fields = [
            'priority', 'notification_preferences', 'notes',
            'is_public', 'is_active'
        ]
    
    def update(self, instance, validated_data):
        """Update wishlist item"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class WishlistSettingsUpdateSerializer(serializers.ModelSerializer):
    """Wishlist settings update serializer"""
    class Meta:
        model = WishlistSettings
        fields = [
            'auto_add', 'max_items', 'notification_preferences',
            'privacy_settings'
        ]
    
    def update(self, instance, validated_data):
        """Update wishlist settings"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class WishlistBulkActionSerializer(serializers.Serializer):
    """Wishlist bulk action serializer"""
    action = serializers.ChoiceField(
        choices=['add', 'remove', 'move_to_cart', 'clear'],
        required=True
    )
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    wishlist_item_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    def validate(self, data):
        """Validate bulk action data"""
        action = data['action']
        
        if action in ['add', 'remove'] and not data.get('product_ids'):
            raise serializers.ValidationError(
                "product_ids required for add/remove actions"
            )
        
        if action in ['move_to_cart'] and not data.get('wishlist_item_ids'):
            raise serializers.ValidationError(
                "wishlist_item_ids required for move_to_cart action"
            )
        
        return data
    
    def save(self):
        """Execute bulk action"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user = self.context['request'].user
        action = self.validated_data['action']
        
        if action == 'add':
            # Add products to wishlist
            product_ids = self.validated_data['product_ids']
            from api.models.product import Product
            
            for product_id in product_ids:
                try:
                    product = Product.objects.get(id=product_id)
                    Wishlist.objects.get_or_create(
                        user=user,
                        product=product,
                        defaults={
                            'priority': 0,
                            'is_active': True,
                            'is_public': False
                        }
                    )
                except Product.DoesNotExist:
                    continue
        
        elif action == 'remove':
            # Remove products from wishlist
            product_ids = self.validated_data['product_ids']
            Wishlist.objects.filter(
                user=user,
                product_id__in=product_ids
            ).delete()
        
        elif action == 'move_to_cart':
            # Move wishlist items to cart
            wishlist_item_ids = self.validated_data['wishlist_item_ids']
            wishlist_items = Wishlist.objects.filter(
                id__in=wishlist_item_ids,
                user=user
            )
            
            for item in wishlist_items:
                # Create cart item logic here
                # This would integrate with cart system
                pass
            
            # Remove from wishlist after moving to cart
            wishlist_items.delete()
        
        elif action == 'clear':
            # Clear entire wishlist
            Wishlist.objects.filter(user=user).delete()
        
        return {'status': 'success', 'action': action}
