# 🏗️ **АРХИТЕКТУРНАЯ ДИАГРАММА LIVECHAT BOT**

## 📊 **Общая архитектура**

```mermaid
graph TB
    subgraph "Presentation Layer"
        TG[Telegram Bot API]
        WEB[Web Interface]
    end
    
    subgraph "Application Layer"
        HANDLERS[Handlers]
        SERVICES[Services]
        EVENTS[Event Handlers]
    end
    
    subgraph "Domain Layer"
        USER[User Domain]
        MSG[Message Domain]
        SUB[Subscription Domain]
        PAY[Payment Domain]
    end
    
    subgraph "Core Layer"
        INTERFACES[Interfaces]
        EVENTS_CORE[Domain Events]
        UOW[Unit of Work]
        BUS[Event Bus]
        DI[DI Container]
    end
    
    subgraph "Infrastructure Layer"
        REPO[Repositories]
        DB[(PostgreSQL)]
        OPENAI[OpenAI API]
        PAYMENT[Payment API]
    end
    
    subgraph "Shared Layer"
        MODELS[Models]
        HELPERS[Helpers]
        SECURITY[Security]
        METRICS[Metrics]
        I18N[I18n]
    end
    
    TG --> HANDLERS
    WEB --> HANDLERS
    HANDLERS --> SERVICES
    SERVICES --> USER
    SERVICES --> MSG
    SERVICES --> SUB
    SERVICES --> PAY
    
    USER --> INTERFACES
    MSG --> INTERFACES
    SUB --> INTERFACES
    PAY --> INTERFACES
    
    INTERFACES --> REPO
    REPO --> DB
    
    SERVICES --> OPENAI
    SERVICES --> PAYMENT
    
    EVENTS --> BUS
    BUS --> EVENTS_CORE
    
    SERVICES --> UOW
    UOW --> REPO
    
    DI --> SERVICES
    DI --> REPO
    
    HANDLERS --> MODELS
    SERVICES --> HELPERS
    HANDLERS --> SECURITY
    SERVICES --> METRICS
    HANDLERS --> I18N
```

## 🔄 **Поток обработки сообщения**

```mermaid
sequenceDiagram
    participant U as User
    participant TG as Telegram
    participant H as Handler
    participant S as Service
    participant UOW as UnitOfWork
    participant R as Repository
    participant DB as Database
    participant AI as OpenAI
    participant EB as EventBus
    
    U->>TG: Send message
    TG->>H: Message event
    H->>S: Process message
    S->>UOW: Start transaction
    UOW->>R: Get user data
    R->>DB: Query user
    DB-->>R: User data
    R-->>UOW: User object
    UOW-->>S: User data
    
    S->>AI: Generate response
    AI-->>S: AI response
    
    S->>UOW: Save message
    UOW->>R: Create message
    R->>DB: Insert message
    DB-->>R: Message created
    R-->>UOW: Message object
    UOW-->>S: Message saved
    
    S->>UOW: Commit transaction
    UOW->>DB: Commit
    DB-->>UOW: Committed
    UOW-->>S: Transaction committed
    
    S->>EB: Publish event
    EB->>H: Event handlers
    
    S-->>H: Response text
    H->>TG: Send response
    TG-->>U: AI response
```

## 🏛️ **Слоистая архитектура**

```mermaid
graph LR
    subgraph "Clean Architecture Layers"
        subgraph "Outer Layer"
            UI[User Interface]
            EXT[External Services]
        end
        
        subgraph "Application Layer"
            UC[Use Cases]
            APP[Application Services]
        end
        
        subgraph "Domain Layer"
            ENT[Entities]
            VAL[Value Objects]
            SRV[Domain Services]
        end
        
        subgraph "Infrastructure Layer"
            REP[Repositories]
            DB[(Database)]
        end
    end
    
    UI --> UC
    EXT --> UC
    UC --> ENT
    UC --> VAL
    UC --> SRV
    SRV --> REP
    REP --> DB
    
    UC -.-> REP
    SRV -.-> REP
```

## 🔧 **Паттерны проектирования**

```mermaid
graph TD
    subgraph "Repository Pattern"
        IR[IRepository]
        UR[UserRepository]
        MR[MessageRepository]
        IR -.-> UR
        IR -.-> MR
    end
    
    subgraph "Unit of Work Pattern"
        IUOW[IUnitOfWork]
        UOW[UnitOfWork]
        IUOW -.-> UOW
    end
    
    subgraph "Event Bus Pattern"
        IEB[IEventBus]
        EB[EventBus]
        EH[Event Handlers]
        IEB -.-> EB
        EB --> EH
    end
    
    subgraph "CQRS Pattern"
        CMD[Commands]
        QRY[Queries]
        CH[Command Handlers]
        QH[Query Handlers]
        CMD --> CH
        QRY --> QH
    end
    
    subgraph "Specification Pattern"
        SPEC[Specifications]
        AND[AndSpecification]
        OR[OrSpecification]
        NOT[NotSpecification]
        SPEC --> AND
        SPEC --> OR
        SPEC --> NOT
    end
    
    subgraph "Factory Pattern"
        FACT[Factories]
        SF[ServiceFactory]
        RF[RepositoryFactory]
        DF[DomainFactory]
        FACT --> SF
        FACT --> RF
        FACT --> DF
    end
```

## 📊 **Метрики и мониторинг**

```mermaid
graph LR
    subgraph "Metrics Collection"
        MC[MetricsCollector]
        MS[MetricsService]
        DB_METRICS[(Bot Metrics)]
    end
    
    subgraph "Event Processing"
        EB[EventBus]
        EH[Event Handlers]
        ES[Event Store]
    end
    
    subgraph "Security Monitoring"
        SV[SecurityValidator]
        SL[SecurityLogger]
        SEC_LOG[(Security Log)]
    end
    
    MC --> MS
    MS --> DB_METRICS
    
    EB --> EH
    EH --> ES
    
    SV --> SL
    SL --> SEC_LOG
    
    EH --> MC
    SV --> MC
```

## 🔒 **Безопасность**

```mermaid
graph TD
    subgraph "Input Validation"
        TS[TextSanitizer]
        SV[SecurityValidator]
        SL[SecurityLogger]
    end
    
    subgraph "Access Control"
        AM[AccessMiddleware]
        ACL[Access Control List]
    end
    
    subgraph "Rate Limiting"
        RL[Rate Limiter]
        DC[Daily Counter]
    end
    
    subgraph "Monitoring"
        SM[Security Metrics]
        AL[Alert System]
    end
    
    TS --> SV
    SV --> SL
    SL --> SM
    
    AM --> ACL
    RL --> DC
    
    SM --> AL
```

## 🌍 **Интернационализация**

```mermaid
graph LR
    subgraph "I18n System"
        IM[I18nManager]
        TR[Translations]
        LG[Language Detection]
    end
    
    subgraph "Supported Languages"
        RU[Russian]
        EN[English]
    end
    
    subgraph "Translation Files"
        RU_TR[ru/translations.json]
        EN_TR[en/translations.json]
    end
    
    IM --> TR
    TR --> RU_TR
    TR --> EN_TR
    
    LG --> RU
    LG --> EN
    
    RU --> RU_TR
    EN --> EN_TR
```

## 🧪 **Тестирование**

```mermaid
graph TD
    subgraph "Architectural Tests"
        AT[Architecture Tests]
        SOLID[SOLID Tests]
        PATTERNS[Pattern Tests]
    end
    
    subgraph "Unit Tests"
        UT[Unit Tests]
        MOCK[Mocks]
        STUB[Stubs]
    end
    
    subgraph "Integration Tests"
        IT[Integration Tests]
        DB_TEST[Database Tests]
        API_TEST[API Tests]
    end
    
    AT --> SOLID
    AT --> PATTERNS
    
    UT --> MOCK
    UT --> STUB
    
    IT --> DB_TEST
    IT --> API_TEST
```

## 📈 **Масштабирование**

```mermaid
graph TB
    subgraph "Horizontal Scaling"
        LB[Load Balancer]
        BOT1[Bot Instance 1]
        BOT2[Bot Instance 2]
        BOT3[Bot Instance 3]
    end
    
    subgraph "Database Scaling"
        DB_MASTER[(Master DB)]
        DB_SLAVE1[(Slave DB 1)]
        DB_SLAVE2[(Slave DB 2)]
    end
    
    subgraph "Caching"
        REDIS[(Redis Cache)]
        MEMORY[Memory Cache]
    end
    
    LB --> BOT1
    LB --> BOT2
    LB --> BOT3
    
    DB_MASTER --> DB_SLAVE1
    DB_MASTER --> DB_SLAVE2
    
    BOT1 --> REDIS
    BOT2 --> REDIS
    BOT3 --> REDIS
    
    BOT1 --> MEMORY
    BOT2 --> MEMORY
    BOT3 --> MEMORY
```
