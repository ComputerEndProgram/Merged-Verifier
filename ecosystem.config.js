module.exports = {
  apps: [
    {
      name: "dtb-verifier",
      script: "/home/ubuntu/.local/bin/dtb-verifier",
      cwd: "/home/ubuntu/DTB-Verifier-new",
      interpreter: "/usr/bin/python3.13",
      env: {
        BOT_PROFILE: "stfc_verifier_alliance",
      },
    },
  ],
};
