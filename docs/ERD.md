# Go Slides – Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │     years       │       │   activities    │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ name            │       │ name            │◄──────│ year_id (FK)    │
│ email (unique)  │       │ active          │       │ title           │
│ password        │       │ created_at      │       │ description     │
│ role            │       └─────────────────┘       │ date           │
│ created_at      │                                 │ type           │
└─────────────────┘                                 │ status         │
        │                                            │ quota          │
        │ (no FK; used by Flask-Login)                │ guideline_file │
        │                                            │ created_at     │
        │                                            └────────┬────────┘
        │                                                     │
        │                                                     │ 1:N
        │                                                     ▼
        │                                            ┌─────────────────┐
        │                                            │  registrants    │
        │                                            ├─────────────────┤
        │                                            │ id (PK)         │
        │                                            │ activity_id(FK) │
        │                                            │ name            │
        │                                            │ school          │
        │                                            │ phone           │
        │                                            │ email           │
        │                                            │ status          │
        │                                            │ created_at      │
        │                                            └────────┬────────┘
        │                                                     │
        │                                                     │ 1:N
        │                                                     ▼
        │                                            ┌─────────────────┐
        │                                            │    gallery      │
        │                                            ├─────────────────┤
        │         ┌─────────────────┐                 │ id (PK)         │
        │         │     about       │                 │ year_id (FK)    │
        │         ├─────────────────┤                 │ activity_id(FK) │
        │         │ id (PK)         │                 │ file            │
        │         │ title           │                 │ caption         │
        │         │ description     │                 │ is_featured     │
        │         │ goals           │                 │ created_at      │
        │         │ location        │                 └─────────────────┘
        │         └─────────────────┘
        │
        │         ┌─────────────────────┐
        │         │ contact_messages     │
        │         ├─────────────────────┤
        │         │ id (PK)             │
        │         │ name                │
        │         │ email               │
        │         │ message             │
        │         │ created_at          │
        │         └─────────────────────┘
```

## Relationships

| From        | To          | Type   | Description                          |
|------------|-------------|--------|--------------------------------------|
| years      | activities  | 1 : N  | One year has many activities         |
| years      | gallery     | 1 : N  | One year has many gallery items      |
| activities | registrants | 1 : N  | One activity has many registrants    |
| activities | gallery     | 1 : N  | One activity has many gallery images |
| users      | (none)      | —      | Admin users; no FK in other tables   |
| about      | (none)      | —      | Singleton; one row                   |
| contact_messages | (none) | —     | Form submissions                     |

## Status / Type Values

- **years.active**: `0` or `1` (only one year should be active)
- **activities.type**: `competition` | `non-competition`
- **activities.status**: `open` | `upcoming` | `closed`
- **registrants.status**: `pending` | `verified`
- **gallery.is_featured**: `0` or `1` (show on homepage)
