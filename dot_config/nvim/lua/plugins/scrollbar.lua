return {
  'petertriho/nvim-scrollbar',
  config = function()
    local colorbuddy = require('colorbuddy')
    local colors = require('neosolarized').setup({}).colors
    require('scrollbar').setup({
      handle = {
        color = colorbuddy.Color.to_vim(colors.base1),
      },
    })
  end,
}
