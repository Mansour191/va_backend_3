# وثائق GraphQL الشاملة لـ VynilArt

## نظرة عامة

هذه الوثيقة تصف جميع الـ queries والـ mutations المتاحة في GraphQL API لمشروع VynilArt، مع تغطية شاملة لكل الجداول والعمليات في قاعدة البيانات.

## 🔍 Queries الشاملة

### 1. المستخدمون والمستثمرون (Users & Investors)

```graphql
# معلومات المستخدم الحالي
query {
  me {
    id
    username
    email
    firstName
    lastName
    isStaff
  }
}

# قائمة المستخدمين (للموظفين فقط)
query {
  users {
    id
    username
    email
    isActive
    dateJoined
  }
}

# المستثمرون فقط (للموظفين فقط)
query {
  investors {
    id
    username
    email
    firstName
    lastName
  }
}
```

### 2. المنتجات (Vinyls)

```graphql
# جميع المنتجات مع التصفية
query {
  products(filter: {isActive: true, isFeatured: true}) {
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

# منتجات مميزة
query {
  featuredProducts {
    id
    nameAr
    basePrice
    images {
      imageUrl
    }
  }
}

# منتجات جديدة
query {
  newProducts {
    id
    nameAr
    basePrice
    createdAt
  }
}

# منتجات مخفضة
query {
  saleProducts {
    id
    nameAr
    basePrice
    discountPercent
  }
}

# البحث المتقدم في المنتجات
query {
  advancedSearch(query: "فينيل", filters: {category_id: 1, min_price: 1000}) {
    id
    nameAr
    basePrice
    category {
      nameAr
    }
  }
}

# منتجات مشابهة
query {
  similarProducts(productId: "1") {
    id
    nameAr
    basePrice
  }
}
```

### 3. الفئات والمواد (Categories & Materials)

```graphql
# جميع الفئات
query {
  categories {
    edges {
      node {
        id
        nameAr
        nameEn
        slug
        icon
        parent {
          nameAr
        }
        children {
          nameAr
          nameEn
        }
      }
    }
  }
}

# فئة محددة
query {
  category(slug: "vinyl-flooring") {
    id
    nameAr
    description
    image
  }
}

# جميع المواد
query {
  materials {
    edges {
      node {
        id
        nameAr
        nameEn
        pricePerM2
        isPremium
        image
      }
    }
  }
}
```

### 4. الطلبات والدفعات (Orders & Payments)

```graphql
# طلبات المستخدم الحالي
query {
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

# طلب محدد بالرقم
query {
  orderByNumber(orderNumber: "ORD-12345678") {
    id
    orderNumber
    status
    totalAmount
    timeline {
      status
      note
      timestamp
      user {
        username
      }
    }
  }
}

# جميع الطلبات (للموظفين)
query {
  orders(filter: {status: "pending"}) {
    edges {
      node {
        id
        orderNumber
        customerName
        totalAmount
        status
      }
    }
  }
}

# دفعة محددة
query {
  payment(id: "1") {
    id
    amount
    status
    method
    transactionId
    order {
      orderNumber
    }
  }
}
```

### 5. السلة والمفضلة (Cart & Wishlist)

```graphql
# عناصر السلة
query {
  myCart {
    id
    product {
      nameAr
      basePrice
      images {
        imageUrl
      }
    }
    quantity
    material {
      nameAr
      pricePerM2
    }
  }
}

# عناصر المفضلة
query {
  myWishlist {
    id
    product {
      nameAr
      basePrice
      images {
        imageUrl
      }
    }
    createdAt
  }
}
```

### 6. التقييمات (Reviews)

```graphql
# جميع التقييمات
query {
  reviews(filter: {rating: 5, isVerified: true}) {
    edges {
      node {
        id
        rating
        comment
        user {
          username
        }
        product {
          nameAr
        }
        createdAt
      }
    }
  }
}

# تقارير التقييم (للموظفين)
query {
  reviewReports(reviewId: "1") {
    id
    reason
    user {
      username
    }
    createdAt
  }
}
```

### 7. التصاميم والمحتوى (Designs & Blog)

```graphql
# جميع التصاميم
query {
  designs(filter: {isFeatured: true, isActive: true}) {
    edges {
      node {
        id
        name
        description
        image
        category {
          nameAr
        }
        user {
          username
        }
        likes
        downloads
      }
    }
  }
}

# فئات التصاميم
query {
  designCategories {
    edges {
      node {
        id
        nameAr
        nameEn
        slug
        description
        image
      }
    }
  }
}

# مقالات المدونة
query {
  blogPosts(filter: {isPublished: true}) {
    edges {
      node {
        id
        titleAr
        titleEn
        slug
        summaryAr
        summaryEn
        featuredImage
        author {
          username
        }
        category {
          nameAr
        }
        views
        publishedAt
      }
    }
  }
}
```

### 8. الإشعارات والتنبيهات (Notifications & Alerts)

```graphql
# إشعارات المستخدم
query {
  notifications(filter: {isRead: false}) {
    edges {
      node {
        id
        title
        message
        type
        isRead
        createdAt
      }
    }
  }
}

# تنبيهات المستخدم
query {
  alerts {
    edges {
      node {
        id
        type
        message
        isActive
        createdAt
      }
    }
  }
}
```

### 9. التحليلات والإحصائيات (Analytics)

```graphql
# ملخص المبيعات
query {
  salesSummary(startDate: "2024-01-01", endDate: "2024-12-31") {
    totalSales
    totalOrders
    averageOrderValue
    topProducts
  }
}

# أفضل المنتجات مبيعاً
query {
  topProducts(limit: 10) {
    id
    nameAr
    basePrice
    stock
  }
}

# إحصائيات العملاء
query {
  customerStats {
    totalCustomers
    activeCustomers
    newCustomersThisMonth
  }
}

# تقرير المخزون
query {
  inventoryReport {
    totalProducts
    activeProducts
    lowStockProducts
  }
}

# نشاط المستخدم
query {
  userActivity(userId: "1") {
    totalOrders
    totalSpent
    favoriteCategories
    lastLogin
  }
}

# تاريخ المشتريات
query {
  purchaseHistory(userId: "1", limit: 10) {
    id
    orderNumber
    totalAmount
    status
    createdAt
  }
}
```

### 10. الكوبونات والخصومات (Coupons)

```graphql
# جميع الكوبونات (للموظفين)
query {
  coupons(filter: {isActive: true}) {
    edges {
      node {
        id
        code
        discountType
        discountValue
        minAmount
        usageLimit
        usedCount
        validFrom
        validTo
      }
    }
  }
}

# التحقق من كوبون
query {
  validateCoupon(code: "SAVE20") {
    id
    code
    discountType
    discountValue
    minAmount
  }
}
```

### 11. النظام والمزامرة (System & Sync)

```graphql
# سجلات المزامرة (للموظفين)
query {
  erpSyncLogs(filter: {status: "completed"}) {
    edges {
      node {
        id
        action
        status
        message
        recordsSynced
        timestamp
      }
    }
  }
}

# تتبع السلوك (للموظفين)
query {
  behaviorTracking {
    edges {
      node {
        id
        user {
          username
        }
        action
        targetType
        targetId
        metadata
        createdAt
      }
    }
  }
}

# التوقعات (للموظفين)
query {
  forecasts {
    edges {
      node {
        id
        product {
          nameAr
        }
        forecastType
        period
        predictedDemand
        confidence
      }
    }
  }
}
```

## 🔧 Mutations الشاملة

### 1. إدارة المنتجات (Product Management)

```graphql
# إنشاء منتج جديد
mutation {
  createProduct(input: {
    nameAr: "فينيل فاخر"
    nameEn: "Premium Vinyl"
    slug: "premium-vinyl"
    basePrice: 2500.00
    descriptionAr: "منتج فينيل عالي الجودة"
    descriptionEn: "High quality vinyl product"
    categoryId: 1
    isFeatured: true
    stock: 100
    tags: ["فينيل", "أرضيات", "عالي الجودة"]
  }) {
    success
    message
    product {
      id
      nameAr
      basePrice
    }
  }
}

# تحديث منتج
mutation {
  updateProduct(input: {
    id: "1"
    basePrice: 3000.00
    isFeatured: false
    stock: 150
  }) {
    success
    message
    product {
      id
      basePrice
      isFeatured
      stock
    }
  }
}

# حذف منتج (تعطيل)
mutation {
  deleteProduct(id: "1") {
    success
    message
  }
}

# تحديث مجموعة منتجات
mutation {
  bulkUpdateProducts(
    productIds: ["1", "2", "3"]
    updates: {
      isFeatured: true
      stock: 200
    }
  ) {
    success
    message
    updatedCount
  }
}
```

### 2. إدارة الفئات (Category Management)

```graphql
# إنشاء فئة جديدة
mutation {
  createCategory(
    nameAr: "أرضيات الفينيل"
    nameEn: "Vinyl Flooring"
    slug: "vinyl-flooring"
    description: "مجموعة أرضيات الفينيل"
    icon: "flooring-icon"
    wastePercent: 10.5
  ) {
    success
    message
    category {
      id
      nameAr
      nameEn
      slug
    }
  }
}

# تحديث فئة
mutation {
  updateCategory(
    id: "1"
    input: {
      nameAr: "أرضيات الفينيل المحدثة"
      is_active: true
    }
  ) {
    success
    message
    category {
      id
      nameAr
    }
  }
}

# حذف فئة (تعطيل)
mutation {
  deleteCategory(id: "1") {
    success
    message
  }
}
```

### 3. إدارة المواد (Material Management)

```graphql
# إنشاء مادة جديدة
mutation {
  createMaterial(input: {
    nameAr: "فينيل عالي الكثافة"
    nameEn: "High Density Vinyl"
    description: "مادة فينيل عالية الكثافة للأرضيات"
    pricePerM2: 150.00
    isPremium: true
    is_active: true
    properties: "{\"thickness\": \"3mm\", \"warranty\": \"10years\"}"
  }) {
    success
    message
    material {
      id
      nameAr
      pricePerM2
      isPremium
    }
  }
}
```

### 4. إدارة الطلبات (Order Management)

```graphql
# إنشاء طلب جديد
mutation {
  createOrder(input: {
    customerName: "أحمد محمد"
    phone: "01234567890"
    email: "ahmed@example.com"
    shippingAddress: "شارع النصر، القاهرة"
    wilayaId: "16"
    paymentMethod: "cod"
    notes: "التوصيل بعد 6 مساءً"
    items: [
      {
        productId: "1"
        materialId: "1"
        width: 100.0
        height: 200.0
        quantity: 2
      }
    ]
  }) {
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

# تحديث حالة الطلب
mutation {
  updateOrderStatus(input: {
    id: "1"
    status: "confirmed"
    notes: "تم تأكيد الطلب وجاري التحضير"
  }) {
    success
    message
    order {
      id
      status
      timeline {
        status
        note
        timestamp
      }
    }
  }
}
```

### 5. إدارة الدفعات (Payment Management)

```graphql
# معالجة دفعة
mutation {
  processPayment(input: {
    orderId: "1"
    amount: 5000.00
    method: "card"
    transactionId: "TXN123456789"
  }) {
    success
    message
    payment {
      id
      amount
      status
      method
      transactionId
    }
  }
}
```

### 6. التفاعلات مع المستخدمين (User Interactions)

```graphql
# إضافة إلى السلة
mutation {
  addToCart(productId: "1", materialId: "1", quantity: 2) {
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

# إزالة من السلة
mutation {
  removeFromCart(cartItemId: "1") {
    success
    message
  }
}

# إضافة إلى المفضلة
mutation {
  addToWishlist(productId: "1") {
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

# إزالة من المفضلة
mutation {
  removeFromWishlist(productId: "1") {
    success
    message
  }
}

# إنشاء تقييم
mutation {
  createReview(input: {
    productId: "1"
    rating: 5
    comment: "منتج ممتاز وجودة عالية!"
  }) {
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

# تحديث تقييم
mutation {
  updateReview(
    reviewId: "1"
    rating: 4
    comment: "منتج جيد جداً"
  ) {
    success
    message
    review {
      id
      rating
      comment
    }
  }
}
```

### 7. إدارة الكوبونات (Coupon Management)

```graphql
# إنشاء كوبون جديد
mutation {
  createCoupon(input: {
    code: "SAVE20"
    discountType: "percentage"
    discountValue: 20.0
    minAmount: 1000.0
    usageLimit: 100
    validFrom: "2024-01-01T00:00:00Z"
    validTo: "2024-12-31T23:59:59Z"
    is_active: true
  }) {
    success
    message
    coupon {
      id
      code
      discountType
      discountValue
    }
  }
}
```

### 8. إدارة المحتوى (Content Management)

```graphql
# إنشاء تصميم جديد
mutation {
  createDesign(input: {
    name: "تصميم حديث"
    description: "تصميم أرضيات فينيل حديث"
    image: "/images/design1.jpg"
    categoryId: "1"
    isFeatured: true
    tags: ["حديث", "أرضيات", "فينيل"]
    status: "approved"
  }) {
    success
    message
    design {
      id
      name
      status
    }
  }
}

# إنشاء مقال مدونة
mutation {
  createBlogPost(input: {
    titleAr: "كيفية اختيار أرضيات الفينيل"
    titleEn: "How to Choose Vinyl Flooring"
    slug: "how-to-choose-vinyl-flooring"
    contentAr: "محتوى المقال بالعربية..."
    contentEn: "Article content in English..."
    summaryAr: "ملخص المقال"
    summaryEn: "Article summary"
    categoryId: "1"
    featuredImage: "/images/blog1.jpg"
    tags: ["فينيل", "أرضيات", "دليل"]
    is_published: true
  }) {
    success
    message
    blogPost {
      id
      titleAr
      slug
      isPublished
    }
  }
}
```

### 9. الإشعارات (Notifications)

```graphql
# إرسال إشعار
mutation {
  sendNotification(input: {
    userId: "1"
    title: "طلبك جاهز"
    message: "طلبك رقم ORD-12345678 جاهز للتوصيل"
    type: "success"
    data: "{\"orderId\": \"1\", \"orderNumber\": \"ORD-12345678\"}"
  }) {
    success
    message
    notification {
      id
      title
      message
      type
    }
  }
}
```

## 📊 أمثلة متقدمة

### مثال كامل لعملية شراء

```graphql
# 1. البحث عن منتج
query SearchProducts {
  advancedSearch(query: "فينيل", filters: {category_id: 1}) {
    id
    nameAr
    basePrice
    images {
      imageUrl
    }
  }
}

# 2. إضافة إلى السلة
mutation AddToCart {
  addToCart(productId: "1", quantity: 2) {
    success
    cartItem {
      id
      quantity
    }
  }
}

# 3. إنشاء طلب
mutation CreateOrder {
  createOrder(input: {
    customerName: "محمد أحمد"
    phone: "01234567890"
    shippingAddress: "شارع الجلاء، القاهرة"
    paymentMethod: "card"
    items: [
      {
        productId: "1"
        width: 100.0
        height: 200.0
        quantity: 2
      }
    ]
  }) {
    success
    order {
      id
      orderNumber
      totalAmount
    }
  }
}

# 4. معالجة الدفع
mutation ProcessPayment {
  processPayment(input: {
    orderId: "1"
    amount: 5000.00
    method: "card"
    transactionId: "TXN123456789"
  }) {
    success
    payment {
      id
      status
    }
  }
}
```

### مثال لإدارة المخزون

```graphql
# 1. عرض تقرير المخزون
query InventoryReport {
  inventoryReport {
    totalProducts
    activeProducts
    lowStockProducts
  }
}

# 2. تحديث منتجات منخفضة المخزون
mutation BulkUpdate {
  bulkUpdateProducts(
    productIds: ["1", "2", "3"]
    updates: {
      stock: 500
      is_active: true
    }
  ) {
    success
    updatedCount
  }
}
```

## 🔐 الصلاحيات والأمان

### مستويات الصلاحيات

1. **عام**: لا يتطلب مصادقة
2. **مصادق**: يجب تسجيل الدخول
3. **موظف**: يجب أن يكون لدى المستخدم صلاحيات الموظفين
4. **مستثمر**: يجب أن ينتمي المستخدم لمجموعة المستثمرين

### أمثلة على الصلاحيات

```graphql
# يتطلب مصادقة
query {
  myOrders {
    id
    orderNumber
  }
}

# يتطلب صلاحيات الموظفين
mutation {
  createProduct(input: {...}) {
    success
  }
}

# يتطلب صلاحيات المستثمرين
query {
  investors {
    id
    username
    email
  }
}
```

## 🚀 استخدام الـ API

### نقاط النهاية

- **الرئيسي**: `/graphql/` - واجهة GraphiQL التفاعلية
- **الدفعات**: `/graphql/batch/` - للعمليات المتعددة
- **الخاص**: `/graphql/private/` - للإنتاج بدون واجهة

### المصادقة

```bash
# إضافة التوكن في الهيدر
Authorization: Bearer <your_jwt_token>
```

هذه الوثيقة تغطي جميع العمليات المتاحة في GraphQL API لمشروع Vynilart، مع أمثلة عملية لكل نوع من العمليات.
