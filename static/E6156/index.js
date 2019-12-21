function login_using_fb_google()
{
    window.location.href = 'https://tse-final.auth.us-east-1.amazoncognito.com/login?client_id=8l08204jb7op0c3fbiv4io1hu&response_type=token&scope=aws.cognito.signin.user.admin+email+openid+phone+profile&redirect_uri=https://tse-frontend-shubham.s3.amazonaws.com/static/E6156/index.html';
    console.log("hello - will now get the token from the URL");
}