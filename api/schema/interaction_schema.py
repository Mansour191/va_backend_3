"""
Interaction Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, DateTime, ID, JSONString
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Count, Avg
from decimal import Decimal


class ReviewType(DjangoObjectType):
    """Review type"""
    id = graphene.ID(required=True)
    user = Field(lambda: UserType)
    product = Field(lambda: ProductType)
    
    # Rating and content
    rating = Int()
    title = String()
    comment = String()
    
    # Media attachments
    images = List(String)
    video_url = String()
    
    # Verification and status
    is_verified = Boolean()
    is_featured = Boolean()
    is_approved = Boolean()
    
    # Engagement
    helpful_count = Int()
    not_helpful_count = Int()
    
    # Purchase verification
    verified_purchase = Boolean()
    order_item = Field(lambda: OrderItemType)
    
    # Moderation
    reported_count = Int()
    moderation_notes = String()
    
    # Computed fields
    is_helpful = Boolean()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = Review
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'product': ['exact'],
            'rating': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'is_verified': ['exact'],
            'is_featured': ['exact'],
            'is_approved': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_is_helpful(self, info):
        """Check if review is considered helpful"""
        total_votes = self.helpful_count + self.not_helpful_count
        if total_votes == 0:
            return False
        return (self.helpful_count / total_votes) >= 0.7


class ReviewReportType(DjangoObjectType):
    """Review report type"""
    id = graphene.ID(required=True)
    review = Field(ReviewType)
    user = Field(lambda: UserType)
    reason = String()
    
    # Status
    status = String()
    
    # Moderator action
    moderator_notes = String()
    moderator = Field(lambda: UserType)
    action_taken = String()
    
    created_at = DateTime()
    reviewed_at = DateTime()

    class Meta:
        model = ReviewReport
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'review': ['exact'],
            'user': ['exact'],
            'status': ['exact'],
            'reason': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }


class BehaviorTrackingType(DjangoObjectType):
    """Behavior tracking type"""
    id = graphene.ID(required=True)
    user = Field(lambda: UserType)
    session_id = String()
    
    # Action details
    action = String()
    target_type = String()
    target_id = Int()
    
    # Context and metadata
    metadata = JSONString()
    
    # Technical information
    ip_address = String()
    user_agent = String()
    referrer = String()
    
    # Location (if available)
    country = String()
    city = String()
    
    # Device information
    device_type = String()
    browser = String()
    operating_system = String()
    
    # Timing
    duration = Int()
    created_at = DateTime()

    class Meta:
        model = BehaviorTracking
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'session_id': ['exact'],
            'action': ['exact'],
            'target_type': ['exact'],
            'target_id': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'ip_address': ['exact'],
        }


class ConversationHistoryType(DjangoObjectType):
    """Conversation history type"""
    id = graphene.ID(required=True)
    session_id = String()
    user = Field(lambda: UserType)
    
    # Message content
    role = String()
    message = String()
    
    # Source and context
    source = String()
    language = String()
    
    # AI-specific fields
    confidence = Float()
    model_used = String()
    processing_time = Float()
    
    # Metadata and context
    metadata = JSONString()
    context = JSONString()
    
    # Feedback and quality
    user_rating = Int()
    user_feedback = String()
    is_helpful = Boolean()
    
    # Moderation
    is_flagged = Boolean()
    flag_reason = String()
    moderator_notes = String()
    
    created_at = DateTime()

    class Meta:
        model = ConversationHistory
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'session_id': ['exact'],
            'user': ['exact'],
            'role': ['exact'],
            'source': ['exact'],
            'language': ['exact'],
            'is_flagged': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_is_from_user(self, info):
        """Check if message is from user"""
        return self.role == 'user'

    def resolve_is_from_assistant(self, info):
        """Check if message is from assistant"""
        return self.role == 'assistant'


# Input Types
class ReviewInput(graphene.InputObjectType):
    """Input for review creation and updates"""
    product_id = ID(required=True)
    rating = Int(required=True)
    title = String()
    comment = String()
    
    # Media attachments
    images = List(String)
    video_url = String()
    
    # Purchase verification
    order_item_id = ID()


class ReviewUpdateInput(graphene.InputObjectType):
    """Input for review updates"""
    id = ID(required=True)
    rating = Int()
    title = String()
    comment = String()
    images = List(String)
    video_url = String()


class ReviewReportInput(graphene.InputObjectType):
    """Input for review report creation"""
    review_id = ID(required=True)
    reason = String(required=True)
    description = String()


class ConversationHistoryInput(graphene.InputObjectType):
    """Input for conversation history"""
    session_id = String(required=True)
    role = String(required=True)
    message = String(required=True)
    
    # Source and context
    source = String()
    language = String(default_value='ar')
    
    # AI-specific fields
    confidence = Float()
    model_used = String()
    processing_time = Float()
    
    # Metadata and context
    metadata = JSONString()
    context = JSONString()


# Mutations
class CreateReview(Mutation):
    """Create a new review"""
    
    class Arguments:
        input = ReviewInput(required=True)

    success = Boolean()
    message = String()
    review = Field(ReviewType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.interaction import Review
            from api.models.product import Product
            from api.models.order import OrderItem
            
            user = info.context.user
            
            if not user.is_authenticated:
                return CreateReview(
                    success=False,
                    message="Authentication required",
                    errors=["Authentication required"]
                )
            
            product = Product.objects.get(id=input['product_id'])
            
            # Check if user already reviewed this product
            existing_review = Review.objects.filter(
                user=user,
                product=product
            ).first()
            
            if existing_review:
                return CreateReview(
                    success=False,
                    message="You have already reviewed this product",
                    errors=["You have already reviewed this product"]
                )
            
            # Handle order item for purchase verification
            order_item = None
            if 'order_item_id' in input:
                order_item = OrderItem.objects.get(id=input['order_item_id'])
            
            review = Review.objects.create(
                user=user,
                product=product,
                rating=input['rating'],
                title=input.get('title'),
                comment=input.get('comment'),
                images=input.get('images', []),
                video_url=input.get('video_url'),
                verified_purchase=bool(order_item),
                order_item=order_item
            )
            
            return CreateReview(
                success=True,
                message="Review created successfully",
                review=review
            )
            
        except Exception as e:
            return CreateReview(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateReview(Mutation):
    """Update an existing review"""
    
    class Arguments:
        input = ReviewUpdateInput(required=True)

    success = Boolean()
    message = String()
    review = Field(ReviewType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.interaction import Review
            
            user = info.context.user
            
            review = Review.objects.get(id=input['id'])
            
            # Check ownership
            if review.user != user:
                return UpdateReview(
                    success=False,
                    message="Access denied",
                    errors=["Access denied"]
                )
            
            # Update fields
            for field, value in input.items():
                if field != 'id' and hasattr(review, field):
                    setattr(review, field, value)
            
            review.save()
            
            return UpdateReview(
                success=True,
                message="Review updated successfully",
                review=review
            )
            
        except Review.DoesNotExist:
            return UpdateReview(
                success=False,
                message="Review not found",
                errors=["Review not found"]
            )
        except Exception as e:
            return UpdateReview(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class ReportReview(Mutation):
    """Report a review"""
    
    class Arguments:
        input = ReviewReportInput(required=True)

    success = Boolean()
    message = String()
    report = Field(ReviewReportType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.interaction import Review, ReviewReport
            
            user = info.context.user
            
            if not user.is_authenticated:
                return ReportReview(
                    success=False,
                    message="Authentication required",
                    errors=["Authentication required"]
                )
            
            review = Review.objects.get(id=input['review_id'])
            
            # Check if already reported
            existing_report = ReviewReport.objects.filter(
                review=review,
                user=user
            ).first()
            
            if existing_report:
                return ReportReview(
                    success=False,
                    message="You have already reported this review",
                    errors=["You have already reported this review"]
                )
            
            report = ReviewReport.objects.create(
                review=review,
                user=user,
                reason=input['reason'],
                description=input.get('description')
            )
            
            return ReportReview(
                success=True,
                message="Review reported successfully",
                report=report
            )
            
        except Review.DoesNotExist:
            return ReportReview(
                success=False,
                message="Review not found",
                errors=["Review not found"]
            )
        except Exception as e:
            return ReportReview(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class AddConversationMessage(Mutation):
    """Add message to conversation history"""
    
    class Arguments:
        input = ConversationHistoryInput(required=True)

    success = Boolean()
    message = String()
    conversation_message = Field(ConversationHistoryType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.interaction import ConversationHistory
            
            user = info.context.user
            
            conversation_message = ConversationHistory.objects.create(
                session_id=input['session_id'],
                user=user if user.is_authenticated else None,
                role=input['role'],
                message=input['message'],
                source=input.get('source'),
                language=input.get('language', 'ar'),
                confidence=input.get('confidence'),
                model_used=input.get('model_used'),
                processing_time=input.get('processing_time'),
                metadata=input.get('metadata', {}),
                context=input.get('context', {})
            )
            
            return AddConversationMessage(
                success=True,
                message="Message added successfully",
                conversation_message=conversation_message
            )
            
        except Exception as e:
            return AddConversationMessage(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class RateConversationMessage(Mutation):
    """Rate a conversation message"""
    
    class Arguments:
        message_id = ID(required=True)
        rating = Int(required=True)
        feedback = String()

    success = Boolean()
    message = String()
    conversation_message = Field(ConversationHistoryType)
    errors = List(String)

    def mutate(self, info, message_id, rating, feedback=None):
        try:
            from api.models.interaction import ConversationHistory
            
            user = info.context.user
            
            if not user.is_authenticated:
                return RateConversationMessage(
                    success=False,
                    message="Authentication required",
                    errors=["Authentication required"]
                )
            
            message = ConversationHistory.objects.get(id=message_id)
            
            message.add_feedback(rating, feedback)
            
            return RateConversationMessage(
                success=True,
                message="Message rated successfully",
                conversation_message=message
            )
            
        except ConversationHistory.DoesNotExist:
            return RateConversationMessage(
                success=False,
                message="Message not found",
                errors=["Message not found"]
            )
        except Exception as e:
            return RateConversationMessage(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Query Class
class InteractionQuery(ObjectType):
    """Interaction queries"""
    
    # Review queries
    reviews = List(ReviewType)
    review = Field(ReviewType, id=ID(required=True))
    my_reviews = List(ReviewType)
    product_reviews = List(ReviewType, product_id=ID(required=True))
    
    # Review report queries
    review_reports = List(ReviewReportType)
    
    # Behavior tracking queries
    behavior_tracking = List(BehaviorTrackingType)
    user_behavior = List(BehaviorTrackingType, user_id=ID(required=True))
    
    # Conversation history queries
    conversation_history = List(ConversationHistoryType)
    session_conversation = List(ConversationHistoryType, session_id=String(required=True))
    
    def resolve_reviews(self, info):
        """Get all reviews (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return Review.objects.all()
        return []
    
    def resolve_review(self, info, id):
        """Get review by ID"""
        try:
            return Review.objects.get(id=id)
        except Review.DoesNotExist:
            return None
    
    def resolve_my_reviews(self, info):
        """Get current user's reviews"""
        user = info.context.user
        if user.is_authenticated:
            return Review.objects.filter(user=user)
        return []
    
    def resolve_product_reviews(self, info, product_id):
        """Get reviews for specific product"""
        return Review.objects.filter(product_id=product_id, is_approved=True)
    
    def resolve_review_reports(self, info):
        """Get all review reports (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return ReviewReport.objects.all()
        return []
    
    def resolve_behavior_tracking(self, info):
        """Get all behavior tracking (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return BehaviorTracking.objects.all()
        return []
    
    def resolve_user_behavior(self, info, user_id):
        """Get behavior for specific user (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return BehaviorTracking.objects.filter(user_id=user_id)
        return []
    
    def resolve_conversation_history(self, info):
        """Get all conversation history (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return ConversationHistory.objects.all()
        return []
    
    def resolve_session_conversation(self, info, session_id):
        """Get conversation for specific session"""
        return ConversationHistory.objects.filter(session_id=session_id)


# Mutation Class
class InteractionMutation(ObjectType):
    """Interaction mutations"""
    
    create_review = CreateReview.Field()
    update_review = UpdateReview.Field()
    report_review = ReportReview.Field()
    add_conversation_message = AddConversationMessage.Field()
    rate_conversation_message = RateConversationMessage.Field()
