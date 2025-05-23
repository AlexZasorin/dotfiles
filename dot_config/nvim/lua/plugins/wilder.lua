return {
  'gelguy/wilder.nvim',
  event = 'CmdlineEnter',
  build = false,
  dependencies = {
    { 'romgrk/fzy-lua-native', build = 'make' },
    { 'nixprime/cpsm', build = '~/.config/nvim/lua/plugins/install_cpsm.sh' },
    'lambdalisue/nerdfont.vim',
    'nvim-scrollbar',
  },
  config = function()
    local wilder = require('wilder')
    wilder.setup({ modes = { ':', '/', '?' } })

    -- Enable caching for better performance
    wilder.set_option('cache', true)

    -- Set debounce time to avoid unnecessary calculations
    wilder.set_option('debounce', 30) -- milliseconds

    wilder.set_option('pipeline', {
      wilder.branch(
        wilder.python_file_finder_pipeline({
          file_command = function(ctx, arg)
            if string.find(arg, '.') ~= nil then
              return { 'rg', '--files', '--hidden' }
            else
              return { 'rg', '--files' }
            end
          end,
          dir_command = { 'fd', '-td' },
          filters = { 'cpsm_filter' },
        }),
        wilder.substitute_pipeline({
          pipeline = wilder.python_search_pipeline({
            skip_cmdtype_check = 1,
            pattern = wilder.python_fuzzy_pattern({
              start_at_boundary = 0,
            }),
          }),
        }),
        wilder.cmdline_pipeline({
          language = 'python',
          fuzzy = 2,
          fuzzy_filter = wilder.lua_fzy_filter(),
        }),
        {
          wilder.check(function(ctx, x)
            return x == ''
          end),
          wilder.history(),
        },
        wilder.python_search_pipeline({
          pattern = wilder.python_fuzzy_pattern({
            start_at_boundary = 0,
          }),
        })
      ),
    })

    local highlighters = {
      wilder.lua_fzy_highlighter(),
    }

    local colors = require('neosolarized').colors

    local popupmenu_renderer = wilder.popupmenu_renderer(wilder.popupmenu_border_theme({
      max_height = '25%',
      empty_message = wilder.popupmenu_empty_message_with_spinner(),
      highlighter = highlighters,
      highlights = {
        accent = wilder.make_hl('WilderAccent', 'Pmenu', { { a = 1 }, { a = 1 }, { foreground = colors.magenta:to_vim() } }),
      },
      left = {
        ' ',
        wilder.popupmenu_devicons(),
        wilder.popupmenu_buffer_flags({
          flags = ' a + ',
          -- icons = { ['+'] = '', a = '', h = '' },
        }),
      },
      right = {
        ' ',
        wilder.popupmenu_scrollbar({ thumb_hl = 'ScrollbarHandle' }),
      },
    }))

    local wildmenu_renderer = wilder.wildmenu_renderer({
      highlighter = highlighters,
      separator = ' · ',
      left = { ' ', wilder.wildmenu_spinner(), ' ' },
      right = { ' ', wilder.wildmenu_index() },
    })

    wilder.set_option(
      'renderer',
      wilder.renderer_mux({
        [':'] = popupmenu_renderer,
        ['/'] = popupmenu_renderer,
        substitute = wildmenu_renderer,
      })
    )
  end,
}
