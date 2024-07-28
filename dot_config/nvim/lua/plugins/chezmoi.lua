return {
  {
    -- highlighting for chezmoi files template files
    'alker0/chezmoi.vim',
    init = function()
      vim.g['chezmoi#use_tmp_buffer'] = 1
      vim.g['chezmoi#source_dir_path'] = os.getenv('HOME') .. '/.local/share/chezmoi'
    end,
  },
  {
    'xvzc/chezmoi.nvim',
    dependencies = { 'nvim-lua/plenary.nvim' },
    config = function()
      require('chezmoi').setup({
        edit = {
          watch = true,
          force = false,
        },
        notification = {
          on_open = true,
          on_apply = true,
          on_watch = true,
        },
        telescope = {
          select = { '<CR>' },
        },
      })
    end,
  },
}
