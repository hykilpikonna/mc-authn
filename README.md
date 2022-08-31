# mc-authn: Authenticator for Minecraft with Microsoft
 
### Installation

```sh
pip install mc-authn
```

### Usage

#### 1. Create Azure Token

(You can follow [this guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app) for more details)

1. Sign in to the [Azure Portal](https://portal.azure.com/)
2. Click "Azure Active Directory" (the icon should look like Ramiel from EVA 🤔)
3. Click "App registrations" on the left navigation menu
4. Click "New registration" on top left
5. Give it a name
6. For "Supported account types," select "Personal MS accounts only"
7. For "Redirect URI", select "Web" and type "http://localhost:18275"
8. Now you should be in the overview page of your app!
9. You should see a field "Application (client) ID", copy that somewhere
10. Click "Certificates & secrets" on the left navbar
11. In the "Client secrets" tab, click "New client secret"
12. Give it a description
13. For "Expires" select "24 months"
14. Click "Add"
15. There should be "Value" and "Secret ID", copy "Value"
16. Write this in `~/.config/mc-auth/auth_config.yml`:

```yaml
ClientID: Paste the "Application (client) ID" here
ClientSecret: Paste the "Value" you copied here
```

#### 2. Login!

You can now run `mc-auth` to login! After logging in, it will create a text file `~/.config/mc-auth/mc-token.txt` containing your minecraft token.

In your start script for minecraft, add the `--accessToken` argument to the java line used to start minecraft:

```shell
export uuid=$(< ~/.config/mc-auth/mc-uuid.txt)
export auth=$(< ~/.config/mc-auth/mc-token.txt)

java ... net.minecraft.client.main.Main ... \
    --accessToken ${auth} \
    --uuid ${uuid}
```

#### 3. Start Minecraft!

You can now start minecraft!
