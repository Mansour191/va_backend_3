"""
Review Schema for VynilArt API
This module provides GraphQL types and resolvers for Review and ReviewReport models
"""
import graphene
from graphene import relay, ObjectType, Mutation, Field, List, String, Int, Float, Boolean, DateTime, ID
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from ..models import Review, ReviewReport
from .product_schema import ProductType
from .user_schema import UserType

User = get_user_model()


class ReviewType(DjangoObjectType):
    """
    GraphQL type for Review model
    """
    user = Field(UserType)
    product = Field(ProductType)
    
    class Meta:
        model = Review
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'user': ['exact'],
            'product': ['exact'],
            'rating': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'is_verified': ['exact'],
            'helpful_count': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }
    
    def resolve_user(self, info):
        """
        Resolve review user with privacy protection
        """
        if self.user:
            return self.user
        return None


class ReviewReportType(DjangoObjectType):
    """
    GraphQL type for ReviewReport model
    """
    review = Field(ReviewType)
    user = Field(UserType)
    
    class Meta:
        model = ReviewReport
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'review': ['exact'],
            'user': ['exact'],
            'reason': ['exact', 'icontains'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }


class SubmitReview(Mutation):
    """
    Mutation to submit a new review for a product
    """
    class Arguments:
        product_id = ID(required=True, description="Product ID to review")
        rating = Int(required=True, description="Rating from 1 to 5")
        comment = String(required=False, description="Optional review comment")
    
    review = Field(ReviewType)
    success = Boolean()
    message = String()
    
    def mutate(self, info, product_id, rating, comment=None):
        if not info.context.user.is_authenticated:
            return SubmitReview(
                success=False,
                message="Authentication required"
            )
        
        # Validate rating
        if not 1 <= rating <= 5:
            return SubmitReview(
                success=False,
                message="Rating must be between 1 and 5"
            )
        
        try:
            from ..models.product import Product
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return SubmitReview(
                success=False,
                message="Product not found"
            )
        
        # Check if user already reviewed this product
        if Review.objects.filter(user=info.context.user, product=product).exists():
            return SubmitReview(
                success=False,
                message="You have already reviewed this product"
            )
        
        # Create review
        review = Review.objects.create(
            user=info.context.user,
            product=product,
            rating=rating,
            comment=comment or ''
        )
        
        return SubmitReview(
            review=review,
            success=True,
            message="Review submitted successfully"
        )


class UpdateReview(Mutation):
    """
    Mutation to update an existing review
    """
    class Arguments:
        review_id = ID(required=True, description="Review ID to update")
        rating = Int(required=False, description="New rating from 1 to 5")
        comment = String(required=False, description="New review comment")
    
    review = Field(ReviewType)
    success = Boolean()
    message = String()
    
    def mutate(self, info, review_id, rating=None, comment=None):
        if not info.context.user.is_authenticated:
            return UpdateReview(
                success=False,
                message="Authentication required"
            )
        
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return UpdateReview(
                success=False,
                message="Review not found"
            )
        
        # Check if user owns this review or is staff
        if review.user != info.context.user and not info.context.user.is_staff:
            return UpdateReview(
                success=False,
                message="Permission denied"
            )
        
        # Validate rating if provided
        if rating is not None and not 1 <= rating <= 5:
            return UpdateReview(
                success=False,
                message="Rating must be between 1 and 5"
            )
        
        # Update review
        if rating is not None:
            review.rating = rating
        if comment is not None:
            review.comment = comment
        
        review.save()
        
        return UpdateReview(
            review=review,
            success=True,
            message="Review updated successfully"
        )


class DeleteReview(Mutation):
    """
    Mutation to delete a review
    """
    class Arguments:
        review_id = ID(required=True, description="Review ID to delete")
    
    success = Boolean()
    message = String()
    
    def mutate(self, info, review_id):
        if not info.context.user.is_authenticated:
            return DeleteReview(
                success=False,
                message="Authentication required"
            )
        
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return DeleteReview(
                success=False,
                message="Review not found"
            )
        
        # Check if user owns this review or is staff
        if review.user != info.context.user and not info.context.user.is_staff:
            return DeleteReview(
                success=False,
                message="Permission denied"
            )
        
        review.delete()
        
        return DeleteReview(
            success=True,
            message="Review deleted successfully"
        )


class HelpfulReview(Mutation):
    """
    Mutation to increment helpful_count for a review
    """
    class Arguments:
        review_id = ID(required=True, description="Review ID to mark as helpful")
    
    review = Field(ReviewType)
    success = Boolean()
    message = String()
    
    def mutate(self, info, review_id):
        if not info.context.user.is_authenticated:
            return HelpfulReview(
                success=False,
                message="Authentication required"
            )
        
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return HelpfulReview(
                success=False,
                message="Review not found"
            )
        
        # Increment helpful count
        review.helpful_count += 1
        review.save(update_fields=['helpful_count'])
        
        return HelpfulReview(
            review=review,
            success=True,
            message="Review marked as helpful"
        )


class ReportReview(Mutation):
    """
    Mutation to report a review
    """
    class Arguments:
        review_id = ID(required=True, description="Review ID to report")
        reason = String(required=True, description="Reason for reporting")
    
    report = Field(ReviewReportType)
    success = Boolean()
    message = String()
    
    def mutate(self, info, review_id, reason):
        if not info.context.user.is_authenticated:
            return ReportReview(
                success=False,
                message="Authentication required"
            )
        
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return ReportReview(
                success=False,
                message="Review not found"
            )
        
        # Check if user already reported this review
        if ReviewReport.objects.filter(review=review, user=info.context.user).exists():
            return ReportReview(
                success=False,
                message="You have already reported this review"
            )
        
        # Create report
        report = ReviewReport.objects.create(
            review=review,
            user=info.context.user,
            reason=reason
        )
        
        return ReportReview(
            report=report,
            success=True,
            message="Review reported successfully"
        )


class VerifyReview(Mutation):
    """
    Mutation to verify a review (staff only)
    """
    class Arguments:
        review_id = ID(required=True, description="Review ID to verify")
        is_verified = Boolean(required=True, description="Verification status")
    
    review = Field(ReviewType)
    success = Boolean()
    message = String()
    
    def mutate(self, info, review_id, is_verified):
        if not info.context.user.is_authenticated:
            return VerifyReview(
                success=False,
                message="Authentication required"
            )
        
        if not info.context.user.is_staff:
            return VerifyReview(
                success=False,
                message="Staff permissions required"
            )
        
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return VerifyReview(
                success=False,
                message="Review not found"
            )
        
        # Update verification status
        review.is_verified = is_verified
        review.save(update_fields=['is_verified'])
        
        status_text = "verified" if is_verified else "unverified"
        return VerifyReview(
            review=review,
            success=True,
            message=f"Review {status_text} successfully"
        )


# Review Query Class
class ReviewQuery(ObjectType):
    """
    Review queries for GraphQL
    """
    # Individual review queries
    review = relay.Node.Field(ReviewType)
    all_reviews = DjangoFilterConnectionField(ReviewType)
    
    # Review report queries
    review_report = relay.Node.Field(ReviewReportType)
    all_review_reports = DjangoFilterConnectionField(ReviewReportType)
    
    # Product reviews
    product_reviews = List(
        ReviewType,
        product_id=ID(required=True, description="Product ID to get reviews for"),
        verified_only=Boolean(default_value=False, description="Filter only verified reviews")
    )
    
    # User reviews
    user_reviews = List(
        ReviewType,
        user_id=ID(required=False, description="User ID to get reviews for (optional, defaults to current user)")
    )
    
    def resolve_product_reviews(self, info, product_id, verified_only=False):
        """
        Resolve reviews for a specific product
        """
        try:
            from ..models.product import Product
            product = Product.objects.get(id=product_id)
            queryset = Review.objects.filter(product=product)
            
            if verified_only:
                queryset = queryset.filter(is_verified=True)
            
            return queryset.order_by('-created_at')
        except Product.DoesNotExist:
            return []
    
    def resolve_user_reviews(self, info, user_id=None):
        """
        Resolve reviews for a specific user (defaults to current user)
        """
        if not info.context.user.is_authenticated:
            return []
        
        if user_id is None:
            user_id = info.context.user.id
        
        try:
            user = User.objects.get(id=user_id)
            return Review.objects.filter(user=user).order_by('-created_at')
        except User.DoesNotExist:
            return []


# Review Mutation Class
class ReviewMutation(ObjectType):
    """
    Review mutations for GraphQL
    """
    # Review mutations
    submit_review = SubmitReview.Field()
    update_review = UpdateReview.Field()
    delete_review = DeleteReview.Field()
    helpful_review = HelpfulReview.Field()
    report_review = ReportReview.Field()
    verify_review = VerifyReview.Field()


# Export for use in main schema
__all__ = [
    'ReviewQuery',
    'ReviewMutation',
    'ReviewType',
    'ReviewReportType',
]
