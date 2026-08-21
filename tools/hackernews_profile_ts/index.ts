/**
 * HackerNews User Profile & Karma Checker Tool - TypeScript Implementation
 */

interface UserProfile {
  success: boolean;
  username?: string;
  karma?: number;
  created?: string;
  about?: string;
  submitted_count?: number;
  profile_url?: string;
  error?: string;
}

interface Story {
  title: string;
  url: string;
  score: number;
  by: string;
  comments: number;
  hn_url: string;
}

interface TopStoriesResult {
  success: boolean;
  stories?: Story[];
  count?: number;
  error?: string;
}

interface HNUser {
  id: string;
  karma: number;
  created: number;
  about?: string;
  submitted: number[];
}

interface HNItem {
  id: number;
  title?: string;
  url?: string;
  score?: number;
  by?: string;
  descendants?: number;
}

/**
 * Fetches HackerNews user profile including karma, created date, and about info.
 */
async function getUserProfile(username: string): Promise<UserProfile> {
  if (!username || !username.trim()) {
    return { success: false, error: "Username is required." };
  }

  const url = `https://hacker-news.firebaseio.com/v0/user/${username.trim()}.json`;

  try {
    const response = await fetch(url, {
      headers: {
        "User-Agent": "AgentToolsHub/1.0"
      }
    });

    if (!response.ok) {
      if (response.status === 404) {
        return { success: false, error: `HackerNews user '${username}' not found.` };
      }
      return { success: false, error: `HTTP Error ${response.status}: ${response.statusText}` };
    }

    const data: HNUser | null = await response.json() as HNUser | null;

    if (data === null) {
      return { success: false, error: `HackerNews user '${username}' not found.` };
    }

    // Convert Unix timestamp to readable date
    const createdTimestamp = data.created || 0;
    let createdDate = "";
    if (createdTimestamp) {
      createdDate = new Date(createdTimestamp * 1000).toISOString().split('T')[0];
    }

    return {
      success: true,
      username: data.id || username,
      karma: data.karma || 0,
      created: createdDate,
      about: data.about || "",
      submitted_count: data.submitted?.length || 0,
      profile_url: `https://news.ycombinator.com/user?id=${username.trim()}`
    };
  } catch (error) {
    return { 
      success: false, 
      error: `HackerNews query error: ${error instanceof Error ? error.message : String(error)}` 
    };
  }
}

/**
 * Fetches top HackerNews stories.
 */
async function getTopStories(limit: number = 10): Promise<TopStoriesResult> {
  try {
    const response = await fetch("https://hacker-news.firebaseio.com/v0/topstories.json", {
      headers: {
        "User-Agent": "AgentToolsHub/1.0"
      }
    });

    if (!response.ok) {
      return { success: false, error: `Failed to fetch top stories: HTTP ${response.status}` };
    }

    const storyIds: number[] = await response.json() as number[];
    const stories: Story[] = [];

    for (const storyId of storyIds.slice(0, limit)) {
      try {
        const storyResponse = await fetch(
          `https://hacker-news.firebaseio.com/v0/item/${storyId}.json`,
          {
            headers: {
              "User-Agent": "AgentToolsHub/1.0"
            }
          }
        );

        if (storyResponse.ok) {
          const story: HNItem | null = await storyResponse.json() as HNItem | null;
          if (story) {
            stories.push({
              title: story.title || "",
              url: story.url || "",
              score: story.score || 0,
              by: story.by || "",
              comments: story.descendants || 0,
              hn_url: `https://news.ycombinator.com/item?id=${storyId}`
            });
          }
        }
      } catch (error) {
        // Continue with next story if one fails
        console.error(`Failed to fetch story ${storyId}:`, error);
      }
    }

    return {
      success: true,
      stories,
      count: stories.length
    };
  } catch (error) {
    return { 
      success: false, 
      error: `Failed to fetch top stories: ${error instanceof Error ? error.message : String(error)}` 
    };
  }
}

/**
 * Main function that handles both profile and top stories actions
 */
async function runTool(username: string, action: string = "profile", limit: number = 10): Promise<any> {
  if (action === "top") {
    return await getTopStories(limit);
  } else {
    return await getUserProfile(username);
  }
}

// Export functions for module usage
export { getUserProfile, getTopStories, runTool };

// Test execution when run directly
(async () => {
  // Test user profile
  console.log("User Profile:");
  const profileResult = await getUserProfile("pg");
  console.log(JSON.stringify(profileResult, null, 2));

  console.log("\nTop 3 Stories:");
  const storiesResult = await getTopStories(3);
  console.log(JSON.stringify(storiesResult, null, 2));
})();
