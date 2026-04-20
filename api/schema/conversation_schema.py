"""
Conversation Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, DateTime, ID, JSONString, Mutation
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Count, Avg

from api.models.conversation import ConversationHistory


class ConversationHistoryType(DjangoObjectType):
    """Conversation history type"""
    id = graphene.ID(required=True)
    session_id = String()
    user_message = String()
    bot_response = String()
    intent = String()
    entities = JSONString()
    confidence_score = Float()
    message_type = String()
    language = String()
    is_resolved = Boolean()
    escalation_required = Boolean()
    
    # Relations
    user = Field('api.schema.user_schema.UserType')
    
    # Computed fields
    response_time = Float()
    message_length = Int()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = ConversationHistory
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'session_id': ['exact', 'icontains'],
            'intent': ['exact'],
            'message_type': ['exact'],
            'language': ['exact'],
            'is_resolved': ['exact'],
            'escalation_required': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_response_time(self, info):
        """Calculate response time in seconds"""
        # This would typically be calculated based on timestamps
        # For now, return a placeholder
        return 1.5

    def resolve_message_length(self, info):
        """Get message length"""
        return len(self.user_message) if self.user_message else 0


# Input Types
class ConversationHistoryInput(graphene.InputObjectType):
    """Input for conversation history creation"""
    session_id = String(required=True)
    user_message = String(required=True)
    bot_response = String()
    intent = String()
    entities = JSONString()
    confidence_score = Float()
    message_type = String()
    language = String()
    is_resolved = Boolean()
    escalation_required = Boolean()


# Mutations
class CreateConversationHistory(Mutation):
    """Create a new conversation history entry"""
    
    class Arguments:
        input = ConversationHistoryInput(required=True)

    success = Boolean()
    message = String()
    conversation = Field(ConversationHistoryType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            user = info.context.user
            
            # Add user if authenticated
            if user.is_authenticated:
                input['user'] = user
            
            conversation = ConversationHistory.objects.create(**input)
            
            return CreateConversationHistory(
                success=True,
                message="Conversation history created successfully",
                conversation=conversation
            )
            
        except Exception as e:
            return CreateConversationHistory(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateConversationHistory(Mutation):
    """Update an existing conversation history entry"""
    
    class Arguments:
        id = ID(required=True)
        bot_response = String()
        intent = String()
        entities = JSONString()
        confidence_score = Float()
        is_resolved = Boolean()
        escalation_required = Boolean()

    success = Boolean()
    message = String()
    conversation = Field(ConversationHistoryType)
    errors = List(String)

    def mutate(self, info, id, **kwargs):
        try:
            conversation = ConversationHistory.objects.get(id=id)
            
            for field, value in kwargs.items():
                if hasattr(conversation, field) and value is not None:
                    setattr(conversation, field, value)
            
            conversation.save()
            
            return UpdateConversationHistory(
                success=True,
                message="Conversation history updated successfully",
                conversation=conversation
            )
            
        except ConversationHistory.DoesNotExist:
            return UpdateConversationHistory(
                success=False,
                message="Conversation history not found",
                errors=["Conversation history not found"]
            )
        except Exception as e:
            return UpdateConversationHistory(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class ResolveConversation(Mutation):
    """Mark conversation as resolved"""
    
    class Arguments:
        id = ID(required=True)

    success = Boolean()
    message = String()
    conversation = Field(ConversationHistoryType)
    errors = List(String)

    def mutate(self, info, id):
        try:
            conversation = ConversationHistory.objects.get(id=id)
            conversation.is_resolved = True
            conversation.save()
            
            return ResolveConversation(
                success=True,
                message="Conversation marked as resolved",
                conversation=conversation
            )
            
        except ConversationHistory.DoesNotExist:
            return ResolveConversation(
                success=False,
                message="Conversation history not found",
                errors=["Conversation history not found"]
            )
        except Exception as e:
            return ResolveConversation(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Query Class
class ConversationQuery(ObjectType):
    """Conversation queries"""
    
    conversation_histories = List(ConversationHistoryType)
    conversation_history = Field(ConversationHistoryType, id=ID(required=True))
    session_conversations = List(ConversationHistoryType, session_id=String(required=True))
    unresolved_conversations = List(ConversationHistoryType)
    escalated_conversations = List(ConversationHistoryType)
    
    def resolve_conversation_histories(self, info):
        """Get all conversation histories"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return ConversationHistory.objects.all().order_by('-created_at')
        elif user.is_authenticated:
            return ConversationHistory.objects.filter(user=user).order_by('-created_at')
        return []
    
    def resolve_conversation_history(self, info, id):
        """Get conversation history by ID"""
        user = info.context.user
        try:
            conversation = ConversationHistory.objects.get(id=id)
            if user.is_authenticated and (user.is_staff or conversation.user == user):
                return conversation
            return None
        except ConversationHistory.DoesNotExist:
            return None
    
    def resolve_session_conversations(self, info, session_id):
        """Get conversations for specific session"""
        user = info.context.user
        if user.is_authenticated:
            return ConversationHistory.objects.filter(
                session_id=session_id
            ).order_by('created_at')
        return []
    
    def resolve_unresolved_conversations(self, info):
        """Get unresolved conversations"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return ConversationHistory.objects.filter(
                is_resolved=False
            ).order_by('-created_at')
        return []
    
    def resolve_escalated_conversations(self, info):
        """Get escalated conversations"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return ConversationHistory.objects.filter(
                escalation_required=True
            ).order_by('-created_at')
        return []


# Mutation Class
class ConversationMutation(ObjectType):
    """Conversation mutations"""
    
    create_conversation_history = CreateConversationHistory.Field()
    update_conversation_history = UpdateConversationHistory.Field()
    resolve_conversation = ResolveConversation.Field()
