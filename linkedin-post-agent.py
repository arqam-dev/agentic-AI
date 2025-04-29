from flask import Flask, request, jsonify, redirect
import requests

app = Flask(__name__)

CLIENT_ID = "78ohzz6v9j3t9g"
CLIENT_SECRET = "WPL_AP1.hob1Tp6M4WGMxh3w.n4qEpA=="

REDIRECT_URI = "http://localhost:5000/callback"
SCOPE = "w_member_social"

@app.route("/")
def home():
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE}"
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    if 'error' in request.args:
        return f"Error: {request.args.get('error_description')}", 400

    code = request.args.get("code")
    if not code:
        return "Authorization failed: No code returned", 400

    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    response = requests.post(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})

    if response.status_code != 200:
        return f"Token exchange failed: {response.text}", 400

    access_token = response.json().get('access_token')

    author_urn = "urn:li:member:78ohzz6v9j3t9g"

    post_url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0',
        'Content-Type': 'application/json'
    }

    post_data = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "I am happy to share that I am starting a new position."
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    post_response = requests.post(post_url, json=post_data, headers=headers)

    if post_response.status_code == 201:
        return " Post created successfully!", 201
    else:
        return f"Post failed: {post_response.text}", 400

if __name__ == "__main__":
    app.run(debug=True)
