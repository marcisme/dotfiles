return {
  {
    "folke/flash.nvim",
    opts = {
      -- Keep syntax colors intact while Flash is active. Target labels still
      -- receive their normal highlights, but the surrounding text is not dimmed.
      highlight = {
        backdrop = false,
      },
      modes = {
        -- Flash enables the backdrop explicitly for f/F/t/T motions, so this
        -- mode needs its own override in addition to the global setting above.
        char = {
          highlight = {
            backdrop = false,
          },
        },
      },
    },
  },
}
