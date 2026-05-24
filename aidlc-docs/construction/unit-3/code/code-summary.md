# Unit 3: Notification Bell UI — Code Summary

## Status: COMPLETE

## Files Delivered

### Created
1. **`frontend/components/NotificationBell.vue`** — Bell icon button with unread count badge and dropdown panel toggle. Manages polling lifecycle (start on mount, stop on unmount). Handles click-outside to close panel.

2. **`frontend/components/NotificationPanel.vue`** — Dropdown notification panel with:
   - Header with "Mark all read" and "Clear all" action buttons
   - Scrollable notification list (max 20 items)
   - Per-notification: icon (clock for reminder, warning for overdue), message, time-ago, unread indicator
   - Empty state and loading state
   - Click on notification marks it as read

3. **`frontend/composables/useNotifications.ts`** — Singleton composable providing:
   - `notifications`, `unreadCount`, `loading`, `error` (readonly reactive state)
   - `fetchNotifications()` — calls GET /api/notifications
   - `markAsRead(id)` — optimistic PATCH
   - `markAllAsRead()` — optimistic POST
   - `clearAll()` — optimistic DELETE
   - `startPolling()` / `stopPolling()` — 30-second interval

### Modified
4. **`frontend/types/index.ts`** — Added `Notification` and `NotificationsListResponse` interfaces

5. **`frontend/utils/api.ts`** — Added `PATCH` to method union; added `notificationsApi` object

6. **`frontend/pages/dashboard.vue`** — Added `<NotificationBell />` component to navbar

## Integration Notes
- Unit 3 depends on Unit 1's HTTP API endpoints being available at runtime
- During development, the bell will show empty state if the backend notifications endpoints are not running
- No backend changes required for this unit
