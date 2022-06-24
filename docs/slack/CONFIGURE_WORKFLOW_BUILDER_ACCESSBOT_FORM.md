---
layout: default
title: Slack - Accessform Usage
nav_order: 4
parent: Slack
---

# Configure AccessBot Form

If your organization has access to Workflow Builder, you can create an Access Form using that tool (see steps below). If you don't have access to it, you can follow [this tutorial](./CONFIGURE_ACCESS_FORM_BOT.md) teaching you how to set up an AccessForm Bot for free using a more complex method.

## Create the access form with Workflow Builder

First, we need to create the access form via Workflow Builder. To open it, click on the plus sign in the bottom left corner of the Slack chat and search for "Workflow Builder".

![image](https://user-images.githubusercontent.com/20745533/175536751-fd2b5dff-2126-413d-babb-7e6eed1cf03d.png)

![image](https://user-images.githubusercontent.com/20745533/175536931-a9e7cb40-d04b-4989-a5ac-cabc6b159b12.png)

Now, configure your form as follows:

![image](https://user-images.githubusercontent.com/20745533/175537044-69e17cca-539c-4ae7-be89-171d5b03b707.png)

After that you'll have a working form, but we still need to configure the AccessBot to recognize it.

## Set Environment Variable

Now we need to define the environment variable `SDM_ACCESS_FORM_BOT_NICKNAME` with the nickname of the Workflow Builder bot.

To find out their nickname, run the following command in the terminal (in the project root):

```
python3 tools/get-slack-handle.py -d "AccessBot Form" 
```
After running this command, you should see something like this in the terminal:

```
The nick for that user is: @wb_bot_xxxxxxxxxxx
```

After that, set this nickname as the value of the environment variable mentioned above.

```
SDM_ACCESS_FORM_BOT_NICKNAME=@wb_bot_xxxxxxxxxxx
```

## Usage Example

The following gif shows an example of how to use the AccessBot form to request a resource from StrongDM.

![accessbot-form](https://user-images.githubusercontent.com/82273420/163173633-243771d8-a31c-4f79-aaf6-102eb4265286.gif)
