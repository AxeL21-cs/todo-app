# Unit 4: Reminder Form Integration — Code Generation Plan

## Overview
Unit 4 adds reminder time input to the todo form, displays reminder time on todo cards, and provides a visual badge indicating whether a reminder is upcoming or due.

## Status: ALREADY IMPLEMENTED

All Unit 4 files were found to already exist with complete implementations matching the design contracts.

## Files Verified

### Already Created
| File | Description |
|---|---|
| `frontend/components/ReminderBadge.vue` | Visual badge showing "Upcoming" (blue) or "Due" (orange) based on reminder_at vs current time |

### Already Modified
| File | Change |
|---|---|
| `frontend/components/TodoForm.vue` | Has `datetime-local` input for `reminder_at`, ISO conversion helpers, handles both create and edit modes |
| `frontend/components/TodoItem.vue` | Displays formatted `reminder_at` with bell icon, includes `<ReminderBadge>` component |
| `frontend/types/index.ts` | `reminder_at: string | null` on Todo interface; included in TodoCreate and TodoUpdate types |
| `frontend/pages/dashboard.vue` | Create form includes `reminder_at` field with datetime-local input, converts to ISO on submit |

## Contract Compliance
- Todo interface includes `reminder_at: string | null` ✓
- TodoCreate/TodoUpdate include `reminder_at` as optional field ✓
- TodoForm converts local datetime to ISO 8601 UTC on submit ✓
- TodoForm converts ISO 8601 UTC to local datetime for display in edit mode ✓
- ReminderBadge shows "Upcoming" when reminder_at > now ✓
- ReminderBadge shows "Due" when reminder_at <= now ✓
- ReminderBadge hidden when status is "done" or reminder_at is null ✓
- TodoItem displays formatted reminder time ✓
