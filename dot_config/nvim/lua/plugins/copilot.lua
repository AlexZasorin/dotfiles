local on_attach = function(on_attach, name)
  return vim.api.nvim_create_autocmd('LspAttach', {
    callback = function(args)
      local buffer = args.buf
      local client = vim.lsp.get_client_by_id(args.data.client_id)
      if client and (not name or client.name == name) then
        return on_attach(client, buffer)
      end
    end,
  })
end

return {
  -- copilot
  {
    'zbirenbaum/copilot.lua',
    cmd = 'Copilot',
    build = ':Copilot auth',
    event = 'BufReadPost',
    opts = {
      suggestion = { enabled = false },
      panel = { enabled = false },
      filetypes = {
        markdown = true,
        yaml = true,
        help = true,
      },
    },
  },
  -- copilot cmp source
  {
    'nvim-cmp',
    dependencies = {
      {
        'zbirenbaum/copilot-cmp',
        dependencies = 'copilot.lua',
        opts = function()
          local copilot_cmp = require('copilot_cmp')

          local has_words_before = function()
            if vim.api.nvim_buf_get_option(0, 'buftype') == 'prompt' then
              return false
            end
            local line, col = unpack(vim.api.nvim_win_get_cursor(0))
            return col ~= 0 and vim.api.nvim_buf_get_text(0, line - 1, 0, line - 1, col, {})[1]:match('^%s*$') == nil
          end

          -- attach cmp source whenever copilot attaches
          -- fixes lazy-loading issues with the copilot cmp source
          on_attach(function(client)
            copilot_cmp._on_insert_enter({})
          end, 'copilot')

          return {
            mapping = {
              ['<Tab>'] = vim.schedule_wrap(function(fallback)
                if copilot_cmp.visible() and has_words_before() then
                  copilot_cmp.select_next_item({ behavior = copilot_cmp.SelectBehavior.Select })
                else
                  fallback()
                end
              end),
            },
          }
        end,
      },
    },
    opts = function(_, opts)
      table.insert(opts.sources, 1, {
        name = 'copilot',
        group_index = 1,
        priority = 100,
      })
    end,
  },
}

