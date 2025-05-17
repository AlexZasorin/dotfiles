return {
  'pmizio/typescript-tools.nvim',
  dependencies = { 'nvim-lua/plenary.nvim', 'neovim/nvim-lspconfig' },
  opts = {},
  lazy = false,
  config = function()
    -- Disable ts_ls since typescript-tools.nvim is used
    vim.lsp.enable('ts_ls', false)

    local util = require('lspconfig').util
    local is_deno = util.root_pattern('deno.json', 'deno.jsonc')(vim.fn.getcwd()) ~= nil
    local in_templates = string.match(vim.fn.expand('%:p'), '/scaffold/src/templates/') ~= nil

    if is_deno or in_templates then
      return -- Don't setup typescript-tools in Deno projects or template files
    end

    require('typescript-tools').setup({
      settings = {
        tsserver_file_preferences = {
          includeInlayParameterNameHints = 'all',
          includeCompletionsForModuleExports = true,
          quotePreference = 'auto',
        },
        tsserver_format_options = {
          allowIncompleteCompletions = false,
          allowRenameOfImportPath = false,
        },
        jsx_close_tag = {
          enable = true,
          filetypes = { 'javascriptreact', 'typescriptreact' },
        },
      },
      root_dir = util.root_pattern('package.json', 'tsconfig.json'),
      single_file_support = false,
    })
    local keymap_group = vim.api.nvim_create_augroup('TSToolsKeymaps', { clear = true })
    local opts = { noremap = true, silent = true }

    local function setup_keymaps()
      vim.keymap.set('n', '<leader>rf', ':TSToolsRenameFile<CR>', opts)
      vim.keymap.set('n', '<leader>oi', ':TSToolsOrganizeImports<CR>', opts)
      vim.keymap.set('n', '<leader>ru', ':TSToolsRemoveUnused<CR>', opts)
      vim.keymap.set('n', '<leader>ai', ':TSToolsAddMissingImports<CR>', opts)
      vim.keymap.set('n', '<leader>cf', ':TSToolsFixAll<CR>', opts)
      vim.keymap.set('n', '<leader>gfr', ':TSToolsFileReferences<CR>', opts)
      vim.keymap.set('n', 'gsd', ':TSToolsGoToSourceDefinition<CR>', opts)
    end

    local function clear_keymaps()
      local keys = {
        '<leader>rf',
        '<leader>oi',
        '<leader>ru',
        '<leader>ai',
        '<leader>cf',
        '<leader>gfr',
        'gsd',
      }

      for _, key in ipairs(keys) do
        local ok = pcall(vim.keymap.del, 'n', key)
        if not ok then
          vim.notify(string.format('Failed to delete keymap: %s', key), vim.log.levels.WARN)
        end
      end
    end

    vim.api.nvim_create_autocmd('LspAttach', {
      group = keymap_group,
      callback = function(args)
        local client = vim.lsp.get_client_by_id(args.data.client_id)
        if client and client.name == 'typescript-tools' then
          setup_keymaps()
        end
      end,
    })
  end,
}
