"""
Interaction Serializers for VynilArt API
Note: This project uses GraphQL only, but serializers are kept for compatibility
"""
from rest_framework import serializers
from api.models.interaction import (
    Review, ReviewReport, BehaviorTracking, ConversationHistory
)


class ReviewReportSerializer(serializers.ModelSerializer):
    """Review report serializer"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    review_title = serializers.CharField(source='review.title', read_only=True)
    
    class Meta:
        model = ReviewReport
        fields = [
            'id', 'review', 'review_title', 'user', 'user_name',
            'reason', 'description', 'status', 'moderator_notes',
            'moderator', 'action_taken', 'created_at', 'reviewed_at'
        ]
        read_only_fields = ['id', 'created_at', 'reviewed_at']


class ReviewSerializer(serializers.ModelSerializer):
    """Review serializer"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.name_ar', read_only=True)
    is_helpful = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_name', 'product', 'product_name',
            'rating', 'title', 'comment', 'images', 'video_url',
            'is_verified', 'is_featured', 'is_approved',
            'helpful_count', 'not_helpful_count',
            'verified_purchase', 'order_item', 'reported_count',
            'moderation_notes', 'created_at', 'updated_at',
            'is_helpful'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_helpful(self, obj):
        """Check if review is considered helpful"""
        return obj.is_helpful


class BehaviorTrackingSerializer(serializers.ModelSerializer):
    """Behavior tracking serializer"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = BehaviorTracking
        fields = [
            'id', 'user', 'user_name', 'session_id', 'action',
            'target_type', 'target_id', 'metadata', 'ip_address',
            'user_agent', 'referrer', 'country', 'city',
            'device_type', 'browser', 'operating_system',
            'duration', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationHistorySerializer(serializers.ModelSerializer):
    """Conversation history serializer"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    is_from_user = serializers.SerializerMethodField()
    is_from_assistant = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversationHistory
        fields = [
            'id', 'session_id', 'user', 'user_name', 'role',
            'message', 'source', 'language', 'confidence',
            'model_used', 'processing_time', 'metadata',
            'context', 'user_rating', 'user_feedback',
            'is_helpful', 'is_flagged', 'flag_reason',
            'moderator_notes', 'created_at', 'is_from_user',
            'is_from_assistant'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_is_from_user(self, obj):
        """Check if message is from user"""
        return obj.is_from_user
    
    def get_is_from_assistant(self, obj):
        """Check if message is from assistant"""
        return obj.is_from_assistant


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Review creation serializer"""
    class Meta:
        model = Review
        fields = [
            'product', 'rating', 'title', 'comment', 'images',
            'video_url', 'order_item'
        ]
    
    def validate_rating(self, value):
        """Validate rating range"""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def validate(self, data):
        """Validate unique constraint"""
        user = self.context['request'].user
        product = data.get('product')
        
        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError(
                "You have already reviewed this product"
            )
        return data
    
    def create(self, validated_data):
        """Create review"""
        user = self.context['request'].user
        
        # Handle purchase verification
        order_item = validated_data.get('order_item')
        verified_purchase = bool(order_item)
        
        return Review.objects.create(
            user=user,
            verified_purchase=verified_purchase,
            **validated_data
        )


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Review update serializer"""
    class Meta:
        model = Review
        fields = [
            'rating', 'title', 'comment', 'images', 'video_url'
        ]
    
    def validate_rating(self, value):
        """Validate rating range"""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def update(self, instance, validated_data):
        """Update review"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ReviewReportCreateSerializer(serializers.ModelSerializer):
    """Review report creation serializer"""
    class Meta:
        model = ReviewReport
        fields = [
            'review', 'reason', 'description'
        ]
    
    def validate(self, data):
        """Validate unique constraint"""
        user = self.context['request'].user
        review = data.get('review')
        
        if ReviewReport.objects.filter(review=review, user=user).exists():
            raise serializers.ValidationError(
                "You have already reported this review"
            )
        return data
    
    def create(self, validated_data):
        """Create review report"""
        user = self.context['request'].user
        return ReviewReport.objects.create(user=user, **validated_data)


class ConversationHistoryCreateSerializer(serializers.ModelSerializer):
    """Conversation history creation serializer"""
    class Meta:
        model = ConversationHistory
        fields = [
            'session_id', 'role', 'message', 'source',
            'language', 'confidence', 'model_used',
            'processing_time', 'metadata', 'context'
        ]
    
    def create(self, validated_data):
        """Create conversation message"""
        user = self.context['request'].user
        if user.is_authenticated:
            validated_data['user'] = user
        
        return ConversationHistory.objects.create(**validated_data)


class BehaviorTrackingCreateSerializer(serializers.ModelSerializer):
    """Behavior tracking creation serializer"""
    class Meta:
        model = BehaviorTracking
        fields = [
            'action', 'target_type', 'target_id', 'metadata',
            'duration'
        ]
    
    def create(self, validated_data):
        """Create behavior tracking record"""
        request = self.context['request']
        
        # Add automatic fields from request
        validated_data.update({
            'user': request.user if request.user.is_authenticated else None,
            'session_id': getattr(request.session, 'session_key', None),
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referrer': request.META.get('HTTP_REFERER', ''),
        })
        
        return BehaviorTracking.objects.create(**validated_data)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ReviewActionSerializer(serializers.Serializer):
    """Review action serializer"""
    action = serializers.ChoiceField(
        choices=['helpful', 'not_helpful', 'report'],
        required=True
    )
    review_id = serializers.IntegerField(required=True)
    reason = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    
    def validate(self, data):
        """Validate action data"""
        if data['action'] == 'report' and not data.get('reason'):
            raise serializers.ValidationError(
                "Reason is required for report action"
            )
        return data
    
    def save(self):
        """Execute review action"""
        action = self.validated_data['action']
        review_id = self.validated_data['review_id']
        user = self.context['request'].user
        
        try:
            review = Review.objects.get(id=review_id)
            
            if action == 'helpful':
                review.mark_helpful()
                return {'status': 'success', 'message': 'Marked as helpful'}
            
            elif action == 'not_helpful':
                review.mark_not_helpful()
                return {'status': 'success', 'message': 'Marked as not helpful'}
            
            elif action == 'report':
                ReviewReport.objects.create(
                    review=review,
                    user=user,
                    reason=self.validated_data['reason'],
                    description=self.validated_data.get('description', '')
                )
                return {'status': 'success', 'message': 'Review reported'}
        
        except Review.DoesNotExist:
            return {'status': 'error', 'message': 'Review not found'}


class ConversationRatingSerializer(serializers.Serializer):
    """Conversation rating serializer"""
    message_id = serializers.IntegerField(required=True)
    rating = serializers.IntegerField(required=True, min_value=1, max_value=5)
    feedback = serializers.CharField(required=False)
    
    def validate_message_id(self, value):
        """Validate message exists"""
        if not ConversationHistory.objects.filter(id=value).exists():
            raise serializers.ValidationError("Message not found")
        return value
    
    def save(self):
        """Rate conversation message"""
        message_id = self.validated_data['message_id']
        rating = self.validated_data['rating']
        feedback = self.validated_data.get('feedback', '')
        
        try:
            message = ConversationHistory.objects.get(id=message_id)
            message.add_feedback(rating, feedback)
            return {
                'status': 'success',
                'message': 'Message rated successfully',
                'rating': rating
            }
        
        except ConversationHistory.DoesNotExist:
            return {'status': 'error', 'message': 'Message not found'}
