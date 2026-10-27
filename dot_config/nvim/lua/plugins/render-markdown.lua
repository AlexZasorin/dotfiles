return {
  'MeanderingProgrammer/render-markdown.nvim',
  dependencies = { 'nvim-treesitter/nvim-treesitter', 'nvim-mini/mini.nvim' }, -- if you use the mini.nvim suite
  -- dependencies = { 'nvim-treesitter/nvim-treesitter', 'nvim-mini/mini.icons' },        -- if you use standalone mini plugins
  -- dependencies = { 'nvim-treesitter/nvim-treesitter', 'nvim-tree/nvim-web-devicons' }, -- if you prefer nvim-web-devicons
  ---@module 'render-markdown'
  ---@type render.md.UserConfig
  ft = { 'markdown', 'quarto', 'codecompanion' },
  opts = {
    render_modes = true,
    checkbox = {
      left_pad = 1,
      custom = {
        deferred = { raw = '[d]', rendered = '󰔟 ', highlight = 'RenderMarkdownDeferred' },
        in_progress = { raw = '[.]', rendered = '󰦖 ', highlight = 'RenderMarkdownInProgress' },
        cancelled = { raw = '[c]', rendered = '󰜺 ', highlight = 'RenderMarkdownCancelled' },
      },
    },
  },
  config = function(_, opts)
    local colorbuddy = require('colorbuddy')
    local Group, colors = colorbuddy.Group, colorbuddy.colors
    Group.new('RenderMarkdownChecked', colors.green)
    Group.new('RenderMarkdownDeferred', colors.violet)
    Group.new('RenderMarkdownInProgress', colors.yellow)
    Group.new('RenderMarkdownCancelled', colors.base01)
    require('render-markdown').setup(opts)
  end,
}
