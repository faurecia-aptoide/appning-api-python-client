# Pagination

Most list API calls have a maximum limit of results they return in a single response. To retrieve more than that, responses may include a pagination token that you pass with the next request to get the following page.

The token is usually found on the list response object as `nextPageToken`. Pass it in the request parameters for the next call.

```python
request = service.some().list(part='snippet', maxResults=10)
while request is not None:
    response = request.execute()
    # Process response.get('items', [])

    request = service.some().list_next(request, response)
```

For APIs that provide a `list_next()` helper on the resource, use it as above: pass the previous request and response to get the next request, or `None` when there are no more pages. See the API’s reference documentation for the exact parameter name (often `pageToken`) and response field (often `nextPageToken`).
