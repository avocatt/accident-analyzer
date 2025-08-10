# Traefik Basic Authentication Implementation Guide

## Overview
This document describes the implementation of Traefik Basic Authentication for protecting both the API backend and frontend services in the LexIntake application deployed on Coolify.

## Architecture

```
Internet → Traefik Proxy (with Basic Auth) → Protected Services
                ├── Backend API (port 8000)
                └── Frontend UI (port 80)
```

## Implementation Details

### 1. Docker Compose Configuration

The authentication is configured through Docker labels in `docker-compose.yml`:

#### Backend Service Protection
```yaml
backend:
  labels:
    - traefik.http.middlewares.backend-auth.basicauth.users=${BASIC_AUTH_CREDENTIALS}
    - traefik.http.routers.backend.middlewares=backend-auth
```

#### Frontend Service Protection
```yaml
frontend:
  labels:
    - traefik.http.middlewares.frontend-auth.basicauth.users=${BASIC_AUTH_CREDENTIALS}
    - traefik.http.routers.frontend.middlewares=frontend-auth
```

### 2. How It Works

1. **Middleware Definition**: Each service defines its own Basic Auth middleware (`backend-auth` and `frontend-auth`)
2. **Credentials Source**: Both middlewares use the same `${BASIC_AUTH_CREDENTIALS}` environment variable
3. **Router Association**: Each service's router is configured to use its respective auth middleware
4. **Browser Prompt**: When users access either service, they see a browser-native authentication dialog

### 3. Setting Up Credentials

#### Generate Hashed Credentials

Use `htpasswd` to generate credentials in the required format:

```bash
# Install htpasswd if not available
apt-get install apache2-utils  # Debian/Ubuntu
yum install httpd-tools         # RHEL/CentOS
brew install httpd              # macOS

# Generate credentials (replace 'username' with your desired username)
htpasswd -nb username password
```

This outputs: `username:$apr1$xxxxx$yyyyyyyyyyyyy`

#### Configure Environment Variables

Add the generated credentials to your environment:

```bash
# .env file (for local development)
BASIC_AUTH_CREDENTIALS=username:$$apr1$$xxxxx$$yyyyyyyyyyyyy

# Note: Dollar signs ($) must be doubled ($$) in Docker Compose environment variables
```

#### Coolify Configuration

In Coolify's environment variables section:
1. Add variable name: `BASIC_AUTH_CREDENTIALS`
2. Add value: `username:$apr1$xxxxx$yyyyyyyyyyyyy` (single $ in Coolify)
3. Save and redeploy

### 4. Multiple Users Support

To add multiple users, separate credentials with commas:

```bash
BASIC_AUTH_CREDENTIALS=user1:hash1,user2:hash2,user3:hash3
```

Example:
```bash
BASIC_AUTH_CREDENTIALS=admin:$$apr1$$8xz9$$kP3.K2U/,viewer:$$apr1$$9ya2$$mN4.L3V/
```

### 5. Security Considerations

#### Strengths
- **Proxy-Level Protection**: Requests are authenticated before reaching application code
- **Consistent Security**: Both frontend and backend use the same authentication mechanism
- **Standard Protocol**: Uses HTTP Basic Authentication (RFC 7617)
- **No Application Changes**: Authentication is handled entirely at the infrastructure level

#### Limitations
- **Credential Transmission**: Basic Auth sends credentials with every request (base64 encoded)
- **No Session Management**: Cannot log out without closing the browser
- **Limited User Management**: No built-in password reset or user roles
- **Browser Caching**: Browsers cache Basic Auth credentials until closed

#### Best Practices
1. **Always use HTTPS**: Basic Auth credentials are only base64 encoded, not encrypted
2. **Strong Passwords**: Use complex passwords (minimum 12 characters, mixed case, numbers, symbols)
3. **Regular Rotation**: Change credentials periodically
4. **Access Logs**: Monitor Traefik logs for authentication failures
5. **Rate Limiting**: Consider adding rate limiting middleware to prevent brute force attacks

### 6. Testing the Implementation

#### Command Line Testing
```bash
# Test without credentials (should return 401)
curl -I https://lexintake.emreterzi.com

# Test with credentials (should return 200)
curl -u username:password https://lexintake.emreterzi.com

# Test API endpoint
curl -u username:password https://lexintake-api.emreterzi.com/health
```

#### Browser Testing
1. Open the application URL in a browser
2. Enter username and password when prompted
3. Verify both frontend and API endpoints are accessible after authentication

### 7. Troubleshooting

#### Common Issues

**Issue**: 401 Unauthorized despite correct credentials
- **Solution**: Check for proper escaping of $ signs in Docker Compose (use $$)

**Issue**: No authentication prompt appears
- **Solution**: Verify Traefik labels are correctly applied and service is restarted

**Issue**: Authentication works locally but not in production
- **Solution**: Ensure environment variables are properly set in Coolify

**Issue**: Can't generate proper password hash
- **Solution**: Use online htpasswd generators or Docker image: `docker run --rm httpd:alpine htpasswd -nb username password`

### 8. Enhanced Security Options

For production environments, consider these enhancements:

#### Add Rate Limiting
```yaml
labels:
  - traefik.http.middlewares.ratelimit.ratelimit.average=10
  - traefik.http.middlewares.ratelimit.ratelimit.burst=20
  - traefik.http.routers.backend.middlewares=backend-auth,ratelimit
```

#### Add IP Whitelisting
```yaml
labels:
  - traefik.http.middlewares.ipwhitelist.ipwhitelist.sourcerange=10.0.0.0/8,192.168.0.0/16
  - traefik.http.routers.backend.middlewares=backend-auth,ipwhitelist
```

#### Add Security Headers
```yaml
labels:
  - traefik.http.middlewares.securityheaders.headers.stsSeconds=31536000
  - traefik.http.middlewares.securityheaders.headers.stsIncludeSubdomains=true
  - traefik.http.middlewares.securityheaders.headers.stsPreload=true
  - traefik.http.routers.backend.middlewares=backend-auth,securityheaders
```

### 9. Migration to Advanced Authentication

When ready to move beyond Basic Auth, consider:

1. **OAuth2/OIDC**: Integrate with providers like Auth0, Keycloak, or Google
2. **Forward Auth**: Use Traefik's ForwardAuth middleware with custom authentication service
3. **JWT Tokens**: Implement token-based authentication at the application level
4. **mTLS**: Mutual TLS for machine-to-machine authentication

### 10. Monitoring and Logging

#### Enable Traefik Access Logs
```yaml
# In Traefik configuration
accessLog:
  filePath: /var/log/traefik/access.log
  filters:
    statusCodes:
      - "401-403"  # Log authentication failures
```

#### Monitor Authentication Metrics
- Track 401 response codes
- Monitor unique IP addresses attempting authentication
- Alert on repeated authentication failures

## Conclusion

Traefik Basic Authentication provides a simple yet effective security layer for protecting web services. While it has limitations compared to modern authentication methods, it's suitable for:
- Internal applications
- Development/staging environments
- Simple production deployments with limited user base
- Quick security implementation without application changes

For high-security production environments or applications with complex user management needs, consider implementing more advanced authentication solutions.