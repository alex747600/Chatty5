## Endpoints
- `GET /health`: Health check endpoint
- `GET /admin/users`: List all users (admin only)
- `POST /admin/users/{user_id}/block`: Block a user (admin only)
- `POST /admin/users/{user_id}/unblock`: Unblock a user (admin only)
- `PATCH /admin/users/{user_id}/role`: Update user role (0, 1, or 2) (admin only)
- `DELETE /admin/users/{user_id}`: Delete a user with reason (admin only)
- `GET /admin/reports`: List content reports (admin only, optional)
- `DELETE /admin/posts/{post_id}`: Delete a post (admin only)
- `DELETE /admin/comments/{comment_id}`: Delete a comment (admin only)

## Testing
Run unit tests:
```bash
pytest app/tests