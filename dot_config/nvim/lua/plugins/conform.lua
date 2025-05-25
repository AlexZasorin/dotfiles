-- Autoformat
return {
  'stevearc/conform.nvim',
  event = { 'BufWritePre' },
  cmd = { 'ConformInfo' },
  keys = {
    {
      '<leader>f',
      function()
        require('conform').format({ async = true, lsp_format = 'fallback' })
      end,
      mode = '',
      desc = '[f]ormat buffer',
    },
  },
  opts = {
    notify_on_error = false,
    format_on_save = function(bufnr)
      -- Disable "format_on_save lsp_fallback" for languages that don't
      -- have a well standardized coding style. You can add additional
      -- languages here or re-enable it for the disabled ones.
      local disable_filetypes = { c = true, cpp = true }
      if disable_filetypes[vim.bo[bufnr].filetype] then
        return nil
      else
        return {
          timeout_ms = 1000,
          lsp_format = 'fallback',
        }
      end
    end,
    formatters = {
      prettier = {
        require_cwd = true,
      },
      biome = {
        require_cwd = true,
      },
    },
    formatters_by_ft = {
      lua = { 'stylua' },
      html = { 'prettier' },
      jsonnet = { 'jsonnetfmt' },
      markdown = { 'markdownlint' },
      yaml = { 'prettier' },
      json = { 'prettier' },
      jsonc = { 'prettier' },
      javascript = { 'prettier', 'biome', stop_after_first = true },
      typescript = { 'prettier', 'biome', stop_after_first = true },
      typescriptreact = { 'prettier', 'biome', stop_after_first = true },
      javascriptreact = { 'prettier', 'biome', stop_after_first = true },
      nix = { 'alejandra' },
      python = { 'ruff_format' },
      rust = { 'rustfmt', lsp_format = 'fallback' },
      -- Conform can also run multiple formatters sequentially
      -- python = { "isort", "black" },
      --
      -- You can use 'stop_after_first' to run the firs tavailable formatter from the list
      -- is found.
      -- javascript = { "prettierd", "prettier", stop_after_first = true },
    },
  },
}
