# VynilArt GraphQL API Documentation

## Overview

This document describes the comprehensive GraphQL API built for the VynilArt project, focusing on vinyl products management, investor operations, and financial transactions with proper authentication and authorization.

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Authentication Endpoints

- **Login**: Obtain JWT token by sending credentials to your authentication endpoint
- **Refresh**: Refresh expired tokens (if implemented)

## GraphQL Endpoints

- **Main Endpoint**: `/graphql/` - Interactive GraphiQL interface available
- **Batch Endpoint**: `/graphql/batch/` - For multiple queries in one request
- **Private Endpoint**: `/graphql/private/` - No GraphiQL interface, for production use

## Schema Structure

### Core Types

#### User Types
- `UserNode` - Basic user information
- `UserProfileNode` - Extended user profile data

#### Product Types (Vinyls)
- `ProductNode` - Main product/vinyl information
- `ProductImageNode` - Product images
- `ProductVariantNode` - Product variants
- `CategoryNode` - Product categories
- `MaterialNode` - Available materials

#### Order Types (Financial Operations)
- `OrderNode` - Order information with items and payments
- `OrderItemNode` - Individual order items
- `PaymentNode` - Payment records
- `ShippingNode` - Shipping information

#### User Interaction Types
- `CartItemNode` - Shopping cart items
- `WishlistNode` - User wishlist items
- `ReviewNode` - Product reviews
- `NotificationNode` - User notifications

## Queries

### Product/Vinyl Queries

```graphql
# Get all active products with filtering
query GetProducts($filter: ProductNodeFilter) {
  products(filter: $filter) {
    edges {
      node {
        id
        nameAr
        nameEn
        slug
        basePrice
        isFeatured
        isNew
        onSale
        category {
          nameAr
          nameEn
        }
        images {
          imageUrl
          isMain
        }
      }
    }
  }
}

# Get featured products
query GetFeaturedProducts {
  featuredProducts {
    id
    nameAr
    basePrice
    images {
      imageUrl
    }
  }
}

# Search products
query SearchProducts($query: String!) {
  searchProducts(query: $query) {
    id
    nameAr
    nameEn
    descriptionAr
    basePrice
  }
}
```

### Investor/User Queries

```graphql
# Get all users (Staff only)
query GetUsers {
  users {
    id
    username
    email
    firstName
    lastName
    isActive
    isStaff
  }
}

# Get investors only (Staff only)
query GetInvestors {
  investors {
    id
    username
    email
    firstName
    lastName
  }
}

# Get current user info
query GetMe {
  me {
    id
    username
    email
    firstName
    lastName
    isStaff
  }
}
```

### Order/Financial Queries

```graphql
# Get user's orders
query GetMyOrders {
  myOrders {
    id
    orderNumber
    status
    totalAmount
    paymentStatus
    createdAt
    items {
      product {
        nameAr
        basePrice
      }
      quantity
      price
    }
  }
}

# Get specific order by number
query GetOrderByNumber($orderNumber: String!) {
  orderByNumber(orderNumber: $orderNumber) {
    id
    orderNumber
    status
    totalAmount
    paymentStatus
    items {
      product {
        nameAr
      }
      quantity
      price
    }
  }
}
```

### User Data Queries

```graphql
# Get user's cart
query GetMyCart {
  myCart {
    id
    product {
      nameAr
      basePrice
    }
    quantity
    material {
      nameAr
      pricePerM2
    }
  }
}

# Get user's wishlist
query GetMyWishlist {
  myWishlist {
    id
    product {
      nameAr
      basePrice
      images {
        imageUrl
      }
    }
  }
}
```

## Mutations

### Product Management (Staff Only)

```graphql
# Create new product
mutation CreateProduct($input: ProductInput!) {
  createProduct(input: $input) {
    success
    message
    product {
      id
      nameAr
      nameEn
      slug
      basePrice
    }
  }
}
```

### Financial Operations

```graphql
# Create new order
mutation CreateOrder($input: OrderInput!) {
  createOrder(input: $input) {
    success
    message
    order {
      id
      orderNumber
      totalAmount
      status
    }
  }
}

# Process payment
mutation ProcessPayment($input: PaymentInput!) {
  processPayment(input: $input) {
    success
    message
    payment {
      id
      amount
      status
      method
    }
  }
}
```

### User Interactions

```graphql
# Add to cart
mutation AddToCart($productId: Int!, $quantity: Int) {
  addToCart(productId: $productId, quantity: $quantity) {
    success
    message
    cartItem {
      id
      quantity
      product {
        nameAr
      }
    }
  }
}

# Add to wishlist
mutation AddToWishlist($productId: Int!) {
  addToWishlist(productId: $productId) {
    success
    message
    wishlistItem {
      id
      product {
        nameAr
      }
    }
  }
}

# Create review
mutation CreateReview($input: ReviewInput!) {
  createReview(input: $input) {
    success
    message
    review {
      id
      rating
      comment
      product {
        nameAr
      }
    }
  }
}
```

## Permission System

The API implements a comprehensive permission system:

### Permission Levels

1. **Public**: No authentication required
2. **Authenticated**: User must be logged in
3. **Staff**: User must have staff privileges
4. **Investor**: User must belong to investor group

### Protected Operations

- **Product Creation**: Staff only
- **Order Management**: Authenticated users (own orders) or Staff (all orders)
- **Payment Processing**: Authenticated users (own orders) or Staff
- **User Management**: Staff only
- **Investor Data**: Staff and Investor groups only

## Error Handling

The API returns structured errors with specific codes:

- `AUTHENTICATION_ERROR`: Authentication required
- `PERMISSION_ERROR`: Permission denied
- `VALIDATION_ERROR`: Input validation failed
- `INTERNAL_ERROR`: Server error

Example error response:
```json
{
  "errors": [
    {
      "message": "Authentication required",
      "extensions": {
        "code": "AUTHENTICATION_ERROR"
      }
    }
  ]
}
```

## Filtering and Pagination

Most list queries support filtering and pagination through GraphQL connections:

```graphql
query GetProductsWithFilter($first: Int, $after: String, $filter: ProductNodeFilter) {
  products(first: $first, after: $after, filter: $filter) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      node {
        id
        nameAr
        basePrice
      }
    }
  }
}
```

## Real-time Updates

The API supports real-time updates through Django Channels (WebSocket):

- Order status updates
- New notifications
- Stock level changes
- Price updates

## Testing

Use the GraphiQL interface at `/graphql/` to test queries and mutations interactively.

## Development Notes

1. **Authentication**: Always include JWT token for protected operations
2. **Permissions**: Check permission requirements before making requests
3. **Validation**: Ensure all required fields are provided in mutations
4. **Error Handling**: Implement proper error handling in client applications
5. **Rate Limiting**: Consider implementing rate limiting for production

## Security Considerations

1. **JWT Tokens**: Keep tokens secure and implement proper expiration
2. **Input Validation**: All inputs are validated at the server level
3. **Permission Checks**: All operations check user permissions
4. **SQL Injection**: Django ORM provides protection against SQL injection
5. **CSRF Protection**: CSRF protection is enabled for all endpoints

## Performance Optimization

1. **Query Optimization**: Use specific fields instead of requesting all data
2. **Batching**: Use batch endpoint for multiple operations
3. **Caching**: Implement caching for frequently accessed data
4. **Database Indexing**: Proper indexes are defined on important fields

## Future Enhancements

1. **Subscriptions**: Real-time GraphQL subscriptions
2. **File Upload**: GraphQL file upload support
3. **Advanced Analytics**: Complex analytics queries
4. **Multi-tenancy**: Support for multiple organizations
