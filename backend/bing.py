
import json
import os
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

class BingSearchAPI:
    def __init__(self, subscription_key: str, endpoint: str = "https://api.bing.microsoft.com/v7.0/search"):
        """
        Initialize the Bing Search API client.
        
        Args:
            subscription_key: Your Bing API subscription key
            endpoint: Bing Search API endpoint (defaults to v7.0)
        """
        self.subscription_key = subscription_key
        self.endpoint = endpoint
        self.headers = {
            "Ocp-Apim-Subscription-Key": subscription_key,
            "Accept": "application/json"
        }

    def search(self, query: str, count: int = 5) -> List[Dict]:
        """
        Perform a Bing web search and return top results.
        
        Args:
            query: Search query string
            count: Number of results to return (default 5)
            
        Returns:
            List of dictionaries containing search results
        """
        
        # Add site exclusion operators to query
        modified_query = query + " " + " ".join(f"-site:{site}" for site in ["youtube.com", "youtu.be"])
        
        params = {
            "q": modified_query,
            "count": count * 2,  # Request more results since we'll be filtering some out
            "textDecorations": True,
            "textFormat": "HTML"
        }
        
        try:
            response = requests.get(self.endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            
            search_results = response.json()
            
            if "webPages" in search_results and "value" in search_results["webPages"]:
                results = []
                for item in search_results["webPages"]["value"][:count]:
                    results.append({
                        "title": item["name"],
                        "url": item["url"],
                        "snippet": item["snippet"]
                    })
                return results
            return []
            
        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing API response: {e}")
            return []
        
def bing_search(query):

    subscription_key = os.getenv("BING_API_KEY")
    
    # Initialize the API client
    bing_search = BingSearchAPI(subscription_key)

    # perform search
    results = bing_search.search(query,1)

    print(f"Bing search result: {results[0]['snippet']}")
    print(f"URL: {results[0]['url']}")

    parsed_result = parse_with_jina_reader(results[0]['url'])
    
    end_result= results[0]["snippet"] + "\n" + parsed_result

    print("Before truncation: ", len(end_result))

    # cap at 2k char (500 tokens, for OpenAI limit risk)
    end_result = end_result[:2000]

    print("After truncation: ", len(end_result))
    return end_result

def parse_with_jina_reader(url: str) -> Optional[str]:

    """
    Fetches content from a URL using the Jina Reader service.
    
    Args:
        url (str): The URL to fetch content from
        
    Returns:
        Optional[str]: The content of the response if successful, None if failed
        
    Raises:
        requests.RequestException: If there's an error making the request
    """
    try:
        # Construct the full URL
        full_url = f"https://r.jina.ai/{url}"
        
        # Make the request
        response = requests.get(full_url)
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Return the content
        return response.text
        
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None
