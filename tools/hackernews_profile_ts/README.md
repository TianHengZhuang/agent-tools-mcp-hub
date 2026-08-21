# HackerNews Profile & Karma Checker (TypeScript)

Fetches HackerNews user profiles with karma, creation date, and submission count. Also retrieves top stories with scores and comment counts. TypeScript implementation.

## Features

- **User Profile Lookup**: Get karma, join date, about info, and submission count
- **Top Stories**: Fetch current top stories with scores and comment counts
- **No API Key Required**: Uses HackerNews's public Firebase API
- **TypeScript**: Fully typed implementation with modern async/await patterns

## Installation

```bash
npm install
```

## Usage

### Build the project
```bash
npm run build
```

### Run the tool
```bash
npm start
```

### Development mode
```bash
npm run dev
```

## Code Examples

```typescript
// For development (using ts-node)
import { getUserProfile, getTopStories } from './index';

// For production (after build)
// import { getUserProfile, getTopStories } from './dist/index';

// Get user profile
const profile = await getUserProfile("pg");
console.log(profile);
// {
//   "success": true,
//   "username": "pg",
//   "karma": 157836,
//   "created": "2006-10-09",
//   "about": "Bug Fixer...",
//   "submitted_count": 1234,
//   "profile_url": "https://news.ycombinator.com/user?id=pg"
// }

// Get top stories
const stories = await getTopStories(5);
console.log(stories);
```

## Parameters

### getUserProfile(username)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| username | string | Yes | HackerNews username |

### getTopStories(limit)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| limit | number | No | Number of stories (default: 10) |

### runTool(username, action, limit)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| username | string | Yes | HackerNews username |
| action | string | No | 'profile' or 'top' (default: 'profile') |
| limit | number | No | Number of stories for 'top' action (default: 10) |

## API Reference

Uses the official [HackerNews API](https://github.com/HackerNews/API):
- User: `https://hacker-news.firebaseio.com/v0/user/{username}.json`
- Top stories: `https://hacker-news.firebaseio.com/v0/topstories.json`
- Item: `https://hacker-news.firebaseio.com/v0/item/{id}.json`

## License

MIT
