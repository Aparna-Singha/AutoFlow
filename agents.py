import requests
from transformers import pipeline
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv() 


class WebScraper:
    def run(self, task, data=None):
        """Fetch content based on task"""
        try:
            task_lower = task.lower()
            
            # === WEATHER ===
            if "weather" in task_lower:
                return self.get_weather(task)
            
            # === RESEARCH/SEARCH ===
            elif "search" in task_lower or "research" in task_lower:
                return self.web_search(task)
            
            # === NEWS (default) ===
            else:
                return self.get_news(task)
                
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def get_news(self, task):
        """Fetch tech news from NewsAPI"""
        API_KEY = os.getenv("NEWS_API_KEY")
        
        if not API_KEY:
            return "❌ Error: NEWS_API_KEY not found in .env file"
        
        url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&pageSize=5&apiKey={API_KEY}"
        
        response = requests.get(url)
        articles = response.json().get("articles", [])

        if not articles:
            return "No news articles found."

        news = "📰 Latest Tech News:\n\n"
        for i, art in enumerate(articles, 1):
            title = art.get("title", "")
            description = art.get("description", "") or ""
            news += f"{i}. {title}\n   {description}\n\n"

        return news
    
    def get_weather(self, task):
        """Fetch weather - FREE, no API key needed!"""
        # Extract city from task
        city = "Mumbai"  # default
        words = task.split()
        for i, word in enumerate(words):
            if word.lower() in ["for", "in", "of"] and i + 1 < len(words):
                city = words[i + 1]
                break
        
        # Using free wttr.in API (no key needed!)
        try:
            url = f"https://wttr.in/{city}?format=j1"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            current = data["current_condition"][0]
            
            weather = f"""🌤️ Weather in {city.title()}:

🌡️ Temperature: {current["temp_C"]}°C ({current["temp_F"]}°F)
☁️ Condition: {current["weatherDesc"][0]["value"]}
💧 Humidity: {current["humidity"]}%
💨 Wind: {current["windspeedKmph"]} km/h
🧭 Wind Direction: {current["winddir16Point"]}
👁️ Visibility: {current["visibility"]} km
🌡️ Feels Like: {current["FeelsLikeC"]}°C
"""
            return weather
            
        except Exception as e:
            return f"❌ Weather error: {str(e)}"
    
    def web_search(self, task):
        """Simple web search using DuckDuckGo (FREE, no API key!)"""
        try:
            # Extract search query
            query = task.replace("search", "").replace("research", "").strip()
            query = query.replace("for", "").replace("about", "").strip()
            
            if not query:
                query = "latest technology trends"
            
            # Using DuckDuckGo Instant Answer API (free!)
            url = f"https://api.duckduckgo.com/?q={query}&format=json"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            results = f"🔍 Search Results for: {query}\n\n"
            
            # Get abstract
            if data.get("Abstract"):
                results += f"📄 Summary:\n{data['Abstract']}\n\n"
            
            # Get related topics
            if data.get("RelatedTopics"):
                results += "📌 Related Topics:\n"
                for i, topic in enumerate(data["RelatedTopics"][:5], 1):
                    if isinstance(topic, dict) and topic.get("Text"):
                        results += f"{i}. {topic['Text'][:100]}...\n"
            
            # If no results, return a message
            if results == f"🔍 Search Results for: {query}\n\n":
                results += "No detailed results found. Try a more specific query."
            
            return results
            
        except Exception as e:
            return f"❌ Search error: {str(e)}"


class Summarizer:
    def __init__(self):
        print("🔄 Loading summarization model...")
        self.model = pipeline("summarization", model="facebook/bart-large-cnn")
        print("✅ Model loaded!")

    def run(self, task, data=None):
        """Summarize the provided text"""
        try:
            if not data:
                return "❌ No data to summarize"
            
            data = data[:1024]
            
            if len(data) < 100:
                return f"📋 Content:\n{data}"

            result = self.model(
                data, 
                max_length=130, 
                min_length=30,
                do_sample=False
            )[0]["summary_text"]

            formatted = "📋 SUMMARY\n"
            formatted += "=" * 30 + "\n\n"
            
            points = result.split(". ")
            for i, p in enumerate(points[:5], 1):
                if p.strip():
                    formatted += f"{i}. {p.strip()}.\n"

            return formatted
            
        except Exception as e:
            return f"❌ Summarization error: {str(e)}"


class Mailer:
    def run(self, task, data=None):
        """Send email with the content"""
        try:
            sender = os.getenv("SENDER_EMAIL")
            password = os.getenv("SENDER_EMAIL_PASSWORD")
            
            if not sender or not password:
                return "❌ Error: Email credentials not found in .env"
            
            if "to" in task.lower():
                receiver = task.lower().split("to")[-1].strip()
            else:
                receiver = task.strip()
            
            if "@" not in receiver:
                return f"❌ Invalid email: {receiver}"

            msg = MIMEText(data or "No content")
            msg["Subject"] = "🤖 Automated Report"
            msg["From"] = sender
            msg["To"] = receiver

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            server.quit()

            return f"✅ Email sent to {receiver}!"
            
        except Exception as e:
            return f"❌ Email error: {str(e)}"