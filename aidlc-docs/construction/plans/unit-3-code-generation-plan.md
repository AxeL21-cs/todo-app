# Unit 3: Notification Bell UI — Code Generation Plan

## Overview
Unit 3 implements the frontend notification bell UI: a bell icon with unread badge in the navbar, a dropdown panel showing notifications, and a composable for state management with 30-second polling.

## Files Created
| File | Description |
|---|---|
| `frontend/components/NotificationBell.vue` | Bell icon + unread badge + panel toggle + click-outside close |
| `frontend/components/NotificationPanel.vue` | Dropdown panel with notification list, mark-read, mark-all-read, clear-all actions |
| `frontend/composables/useNotifications.ts` | Reactive state management + polling logic + optimistic updates |

## Files Modified
| File | Change |
|---|---|
| `frontend/types/index.ts` | Added `Notification` interface and `NotificationsListResponse` interface |
| `frontend/utils/api.ts` | Added `PATCH` to FetchOptions method union; added `notificationsApi` object with list/markAsRead/markAllAsRead/clearAll |
| `frontend/pages/dashboard.vue` | Added `<NotificationBell />` to navbar (right side actions, before DarkModeToggle) |

## Design Decisions
1. **Shared state via module-level refs**: The composable uses module-level `ref()` so all components share the same notification state (singleton pattern matching Nuxt composable conventions).
2. **Optimistic updates**: All mutations (markAsRead, markAllAsRead, clearAll) update local state immediately and rollback on API failure.
3. **Click-outside handling**: The bell container uses a document-level click listener to close the panel when clicking outside.
4. **Polling lifecycle**: Polling starts on `NotificationBell` mount and stops on unmount, tied to the dashboard page lifecycle.
5. **Accessible**: Bell button has aria-label, aria-expanded; panel has role="menu"; notification items have role="menuitem"; unread dot has aria-label.

## API Contract Compliance
- `GET /api/notifications` → `notificationsApi.list()` → returns `NotificationsListResponse`
- `PATCH /api/notifications/{id}/read` → `notificationsApi.markAsRead(id)` → returns `Notification`
- `POST /api/notifications/read-all` → `notificationsApi.markAllAsRead()` → returns `{ marked_count: number }`
- `DELETE /api/notifications` → `notificationsApi.clearAll()` → returns void (204)
