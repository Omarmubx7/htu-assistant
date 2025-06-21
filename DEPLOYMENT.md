# 🚀 Deployment Guide - HTU Assistant

This guide will help you deploy the HTU Assistant to GitHub Pages and set up a custom domain.

## 📋 Prerequisites

- GitHub account
- Git installed on your computer
- Domain name (optional, for custom domain)

## 🔧 Step 1: Create GitHub Repository

1. **Go to GitHub.com** and sign in
2. **Click "New repository"** or the "+" icon
3. **Repository name**: `atharprojects` (or your preferred name)
4. **Description**: "HTU Assistant - Smart chatbot for course info and professor office hours"
5. **Make it Public** (required for free GitHub Pages)
6. **Don't initialize** with README (we already have one)
7. **Click "Create repository"**

## 🔗 Step 2: Connect Local Repository to GitHub

Run these commands in your terminal:

```bash
# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/atharprojects.git

# Push your code to GitHub
git branch -M main
git push -u origin main
```

## 🌐 Step 3: Enable GitHub Pages

1. **Go to your repository** on GitHub
2. **Click "Settings"** tab
3. **Scroll down to "Pages"** in the left sidebar
4. **Under "Source"**, select "Deploy from a branch"
5. **Branch**: Select "main"
6. **Folder**: Select "/ (root)"
7. **Click "Save"**

Your site will be available at: `https://YOUR_USERNAME.github.io/atharprojects/`

## 🎯 Step 4: Custom Domain Setup (Optional)

### Option A: Using htu-assistant.com

1. **Purchase the domain** from a registrar (Namecheap, GoDaddy, etc.)
2. **Add DNS records**:
   - **Type**: CNAME
   - **Name**: `@` or `www`
   - **Value**: `YOUR_USERNAME.github.io`
   - **TTL**: 3600 (or default)

3. **In GitHub repository**:
   - Go to Settings > Pages
   - In "Custom domain" field, enter: `htu-assistant.com`
   - Check "Enforce HTTPS"
   - Click "Save"

4. **The CNAME file is already created** in your repository

### Option B: Using a different domain

1. **Purchase your preferred domain**
2. **Update the CNAME file**:
   ```bash
   # Edit the CNAME file
   echo "your-domain.com" > CNAME
   git add CNAME
   git commit -m "Update custom domain"
   git push
   ```

3. **Add DNS records** as in Option A
4. **Update GitHub Pages settings** with your domain

## 🔄 Step 5: Update README with Your URL

Edit the `README.md` file and replace:
- `yourusername` with your actual GitHub username
- Update the live demo URL

## 📱 Step 6: Test Your Deployment

1. **Wait 5-10 minutes** for GitHub Pages to build
2. **Visit your site**: `https://YOUR_USERNAME.github.io/atharprojects/`
3. **Test all features**:
   - Dark mode toggle
   - Course searches (CS101, CS201)
   - Professor searches
   - Quick action buttons

## 🛠️ Troubleshooting

### Site not loading?
- Check if GitHub Pages is enabled in repository settings
- Verify the branch and folder settings
- Wait a few more minutes for the build to complete

### Custom domain not working?
- Check DNS propagation (can take up to 48 hours)
- Verify CNAME record is correct
- Ensure HTTPS is enforced in GitHub settings

### Features not working?
- Check browser console for JavaScript errors
- Verify all files are committed and pushed
- Test in incognito/private browsing mode

## 🔄 Updating Your Site

To update your site:

```bash
# Make your changes
# Then commit and push
git add .
git commit -m "Update description"
git push
```

GitHub Pages will automatically rebuild and deploy your changes.

## 📊 Analytics (Optional)

To add Google Analytics:

1. **Create a Google Analytics account**
2. **Get your tracking ID** (GA_MEASUREMENT_ID)
3. **Add this script** to the `<head>` section of `index.html`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🎉 Congratulations!

Your HTU Assistant is now live and accessible to students and staff worldwide!

### Your URLs:
- **GitHub Pages**: `https://YOUR_USERNAME.github.io/atharprojects/`
- **Custom Domain**: `https://htu-assistant.com` (after DNS setup)

### Next Steps:
- Share the URL with HTU students and staff
- Monitor usage and feedback
- Consider adding more courses and professors
- Implement additional features based on user requests

---

**Need help?** Create an issue in your GitHub repository or contact the development team. 