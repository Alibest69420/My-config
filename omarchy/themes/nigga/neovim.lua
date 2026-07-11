return {
  {
    "bjarneo/aether.nvim",
    branch = "v3",
    name = "aether",
    priority = 1000,
    opts = {
      colors = {
        bg         = "#14000a",
        dark_bg    = "#0f0008",
        darker_bg  = "#0a0005",
        lighter_bg = "#2c1a23",

        fg         = "#3a1aff",
        dark_fg    = "#2c14bf",
        light_fg   = "#583cff",
        bright_fg  = "#6b53ff",
        muted      = "#5f6167",

        red        = "#ff5d4c",
        yellow     = "#bbba00",
        orange     = "#ff7567",
        green      = "#c3e700",
        cyan       = "#00ced6",
        blue       = "#9d83ff",
        purple     = "#e26bde",
        brown      = "#99463e",

        bright_red    = "#ff7d65",
        bright_yellow = "#d8db00",
        bright_green  = "#74ee00",
        bright_cyan   = "#17edf7",
        bright_blue   = "#c5a1ff",
        bright_purple = "#ff86ff",

        accent               = "#9d83ff",
        cursor               = "#c7efe3",
        foreground           = "#3a1aff",
        background           = "#14000a",
        selection             = "#2c1a23",
        selection_foreground = "#3a1aff",
        selection_background = "#2c1a23",
      },
    },
    -- set up hot reload
    config = function(_, opts)
      require("aether").setup(opts)
      vim.cmd.colorscheme("aether")
      require("aether.hotreload").setup()
    end,
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "aether",
    },
  },
}
