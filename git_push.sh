#!/bin/bash
git init
git add .
git commit -m "Init DXF-First Architecture"

# Tạo repo private bằng API
RESPONSE=$(curl -s -H "Authorization: token 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" \
     -d '{"name": "autocad-ai-mcp", "private": true}' \
     https://api.github.com/user/repos)

# Lấy URL clone
REPO_URL=$(echo $RESPONSE | grep -o '"clone_url": "[^"]*' | grep -o '[^"]*$')

if [ -z "$REPO_URL" ]; then
    echo "Loi tao repo hoac repo da ton tai. Thu repo moi..."
    RESPONSE=$(curl -s -H "Authorization: token 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" \
         -d '{"name": "autocad-mcp-private", "private": true}' \
         https://api.github.com/user/repos)
    REPO_URL=$(echo $RESPONSE | grep -o '"clone_url": "[^"]*' | grep -o '[^"]*$')
fi

echo "REPO URL: $REPO_URL"
if [ -n "$REPO_URL" ]; then
    # Thay the https:// thanh https://TOKEN@
    AUTH_URL=${REPO_URL/https:\/\//https:\/\/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@}
    git remote remove origin 2>/dev/null
    git branch -M main
    git remote add origin $AUTH_URL
    git push -u origin main
else
    echo "Khong the tao repository. Kiem tra token."
fi
