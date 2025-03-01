-- Main LSP Configuration
return {
  'neovim/nvim-lspconfig',
  dependencies = {
    -- Automatically install LSPs and related tools to stdpath for Neovim
    -- Mason must be loaded before its dependents so we need to set it up here.
    -- NOTE: `opts = {}` is the same as calling `require('mason').setup({})`
    { 'williamboman/mason.nvim', opts = {} },
    'williamboman/mason-lspconfig.nvim',
    'WhoIsSethDaniel/mason-tool-installer.nvim',
    'b0o/schemastore.nvim',

    -- Useful status updates for LSP.
    { 'j-hui/fidget.nvim', opts = {} },

    -- Allows extra capabilities provides by nvim-cmp
    'hrsh7th/cmp-nvim-lsp',
    'pmizio/typescript-tools.nvim',
  },
  config = function()
    -- Brief aside: **What is LSP?**
    --
    -- LSP is an initialism you've probably heard, but might not understand what it is.
    --
    -- LSP stands for Language Server Protocol. It's a protocol that helps editors
    -- and language tooling communicate in a standardized fashion.
    --
    -- In general, you have a "server" which is some tool built to understand a particular
    -- language (such as `gopls`, `lua_ls`, `rust_analyzer`, etc.). These Language Servers
    -- (sometimes called LSP servers, but that's kind of like ATM Machine) are standalone
    -- processes that communicate with some "client" - in this case, Neovim!
    --
    -- LSP provides Neovim with features like:
    --  - Go to definition
    --  - Find references
    --  - Autocompletion
    --  - Symbol Search
    --  - and more!
    --
    -- Thus, Language Servers are external tools that must be installed separately from
    -- Neovim. This is where `mason` and related plugins come into play.
    --
    -- If you're wondering about lsp vs treesitter, you can check out the wonderfully
    -- and elegantly composed help section, `:help lsp-vs-treesitter`

    --  This function gets run when an LSP attaches to a particular buffer.
    --    That is to say, every time a new file is opened that is associated with
    --    an lsp (for example, opening `main.rs` is associated with `rust_analyzer`) this
    --    function will be executed to configure the current buffer
    vim.api.nvim_create_autocmd('LspAttach', {
      group = vim.api.nvim_create_augroup('kickstart-lsp-attach', { clear = true }),
      callback = function(event)
        -- NOTE: Remember that Lua is a real programming language, and as such it is possible
        -- to define small helper and utility functions so you don't have to repeat yourself.
        --
        -- In this case, we create a function that lets us more easily define mappings specific
        -- for LSP related items. It sets the mode, buffer and description for us each time.
        local map = function(keys, func, desc, mode)
          mode = mode or 'n'
          vim.keymap.set(mode, keys, func, { buffer = event.buf, desc = 'LSP: ' .. desc })
        end

        -- Jump to the definition of the word under your cursor.
        --  This is where a variable was first declared, or where a function is defined, etc.
        --  To jump back, press <C-t>.
        map('gd', require('telescope.builtin').lsp_definitions, '[g]oto [d]efinition')

        -- Find references for the word under your cursor.
        map('gr', require('telescope.builtin').lsp_references, '[g]oto [r]eferences')

        -- Jump to the implementation of the word under your cursor.
        --  Useful when your language has ways of declaring types without an actual implementation.
        map('gI', require('telescope.builtin').lsp_implementations, '[g]oto [I]mplementation')

        -- Jump to the type of the word under your cursor.
        --  Useful when you're not sure what type a variable is and you want to see
        --  the definition of its *type*, not where it was *defined*.
        map('<leader>D', require('telescope.builtin').lsp_type_definitions, 'Type [D]efinition')

        -- Fuzzy find all the symbols in your current document.
        --  Symbols are things like variables, functions, types, etc.
        map('<leader>ds', require('telescope.builtin').lsp_document_symbols, '[d]ocument [s]ymbols')

        -- Fuzzy find all the symbols in your current workspace.
        --  Similar to document symbols, except searches over your entire project.
        map('<leader>ws', require('telescope.builtin').lsp_dynamic_workspace_symbols, '[w]orkspace [s]ymbols')

        -- Rename the variable under your cursor.
        --  Most Language Servers support renaming across files, etc.
        map('<leader>rn', vim.lsp.buf.rename, '[r]e[n]ame')

        -- Execute a code action, usually your cursor needs to be on top of an error
        -- or a suggestion from your LSP for this to activate.
        map('<leader>ca', vim.lsp.buf.code_action, '[c]ode [a]ction', { 'n', 'x' })

        -- WARN: This is not Goto Definition, this is Goto Declaration.
        --  For example, in C this would take you to the header.
        map('gD', vim.lsp.buf.declaration, '[g]oto [D]eclaration')

        -- The following two autocommands are used to highlight references of the
        -- word under your cursor when your cursor rests there for a little while.
        --    See `:help CursorHold` for information about when this is executed
        --
        -- When you move your cursor, the highlights will be cleared (the second autocommand).
        local client = vim.lsp.get_client_by_id(event.data.client_id)
        if client and client.supports_method(vim.lsp.protocol.Methods.textDocument_documentHighlight) then
          local highlight_augroup = vim.api.nvim_create_augroup('kickstart-lsp-highlight', { clear = false })
          vim.api.nvim_create_autocmd({ 'CursorHold', 'CursorHoldI' }, {
            buffer = event.buf,
            group = highlight_augroup,
            callback = vim.lsp.buf.document_highlight,
          })

          vim.api.nvim_create_autocmd({ 'CursorMoved', 'CursorMovedI' }, {
            buffer = event.buf,
            group = highlight_augroup,
            callback = vim.lsp.buf.clear_references,
          })

          vim.api.nvim_create_autocmd('LspDetach', {
            group = vim.api.nvim_create_augroup('kickstart-lsp-detach', { clear = true }),
            callback = function(event2)
              vim.lsp.buf.clear_references()
              local ok, _ = pcall(vim.api.nvim_clear_autocmds, { group = 'kickstart-lsp-highlight', buffer = event2.buf })
            end,
          })
        end

        -- The following code creates a keymap to toggle inlay hints in your
        -- code, if the language server you are using supports them
        --
        -- This may be unwanted, since they displace some of your code
        if client and client.supports_method(vim.lsp.protocol.Methods.textDocument_inlayHint) then
          map('<leader>th', function()
            vim.lsp.inlay_hint.enable(not vim.lsp.inlay_hint.is_enabled({ bufnr = event.buf }))
          end, '[t]oggle Inlay [h]ints')

          -- Enable inlay hints by default
          -- vim.lsp.inlay_hint.enable()
        end
      end,
    })

    -- Change diagnostic symbols in the sign column (gutter)
    if vim.g.have_nerd_font then
      local signs = { ERROR = '', WARN = '', INFO = '', HINT = '' }
      local diagnostic_signs = {}
      for type, icon in pairs(signs) do
        diagnostic_signs[vim.diagnostic.severity[type]] = icon
      end
      vim.diagnostic.config({ signs = { text = diagnostic_signs } })
    end

    -- LSP servers and clients are able to communicate to each other what features they support.
    --  By default, Neovim doesn't support everything that is in the LSP specification.
    --  When you add nvim-cmp, luasnip, etc. Neovim now has *more* capabilities.
    --  So, we create new capabilities with nvim cmp, and then broadcast that to the servers.
    local capabilities = vim.lsp.protocol.make_client_capabilities()
    capabilities = vim.tbl_deep_extend('force', capabilities, require('cmp_nvim_lsp').default_capabilities())

    local util = require('lspconfig').util

    -- Enable the following language servers
    --  Feel free to add/remove any LSPs that you want here. They will automatically be installed.
    --
    --  Add any additional override configuration in the following tables. Available keys are:
    --  - cmd (table): Override the default command used to start the server
    --  - filetypes (table): Override the default list of associated filetypes for the server
    --  - capabilities (table): Override fields in capabilities. Can be used to disable certain LSP features.
    --  - settings (table): Override the default settings passed when initializing the server.
    --        For example, to see the options for `lua_ls`, you could go to: https://luals.github.io/wiki/settings/
    local servers = {
      -- clangd = {},
      -- gopls = {},
      -- ... etc. See `:help lspconfig-all` for a list of all the pre-configured LSPs
      --
      -- Some languages (like typescript) have entire language plugins that can be useful:
      --    https://github.com/pmizio/typescript-tools.nvim
      --
      -- But for many setups, the LSP (`ts_ls`) will work just fine
      basedpyright = {
        analysis = {
          diagnosticMode = 'workpsace',
          autoSearchPaths = true,
          useLibraryCodeForTypes = true,
        },
        disableOrganzeImports = true,
      },
      bashls = {},
      cssls = {},
      denols = {
        root_dir = function(fname)
          if string.find(fname, 'scaffold/src/templates') then
            return nil
          end
          return util.root_pattern('deno.json', 'deno.jsonc')(fname)
        end,
        single_file_support = false,
      },
      docker_compose_language_service = {},
      dockerls = {},
      eslint = {},
      glint = {
        filetypes = { 'handlebars' },
      },
      graphql = {
        root_dir = util.root_pattern('*.graphql', '.git', '.graphqlrc*', '.graphql.config.*', 'graphql.config.*'),
        filetypes = { 'graphql', 'typescript', 'typescriptreact' },
      },
      html = {},
      jsonnet_ls = {},
      jsonls = {
        init_options = {
          provideFormatter = false,
        },
        settings = {
          json = {
            schemas = require('schemastore').json.schemas(),
            validate = { enable = true },
          },
        },
      },
      lua_ls = {
        -- cmd = {...},
        -- filetypes = { ...},
        -- capabilities = {},
        settings = {
          Lua = {
            completion = {
              callSnippet = 'Replace',
            },
            -- You can toggle below to ignore Lua_LS's noisy `missing-fields` warnings
            diagnostics = { disable = { 'missing-fields' } },
          },
        },
      },
      marksman = {},
      python = {
        analysis = {
          ignore = { '*' },
        },
      },
      ruff = {
        on_attach = function(client, bufnr)
          if client.name == 'ruff' then
            -- Disable hover in favor of Pyright
            client.server_capabilities.hoverProvider = false
            -- Add Ruff-specific keybindings
            local opts = { buffer = bufnr, noremap = true, silent = true }

            -- Organize imports
            vim.keymap.set('n', '<leader>oi', function()
              vim.lsp.buf.code_action({
                context = {
                  only = { 'source.organizeImports' },
                  diagnostics = {},
                },
                apply = true,
              })
            end, opts)

            -- Remove unused imports
            vim.keymap.set('n', '<leader>cf', function()
              vim.lsp.buf.code_action({
                context = {
                  only = { 'source.fixAll' },
                  diagnostics = {},
                },
                apply = true,
              })
            end, opts)
          end
        end,
      },
      rust_analyzer = {
        settings = {
          ['rust-analyzer'] = {
            checkOnSave = {
              command = 'clippy',
            },
            cargo = {
              features = 'all',
            },
          },
        },
      },
      tailwindcss = {},
      tflint = {},
      yamlls = {
        settings = {
          yaml = {
            schemaStore = {
              -- You must disable built-in schemaStore support if you want to use
              -- this plugin and its advanced options like `ignore`.
              enable = false,
              -- Avoid TypeError: Cannot read properties of undefined (reading 'length')
              url = '',
            },
            schemas = require('schemastore').yaml.schemas(),
            customTags = {
              -- https://github.com/aws-cloudformation/cfn-lint-visual-studio-code/blob/3ff0b8cc1bbfc34448c865b54deff8c7d030beba/server/src/cfnSettings.ts
              '!And sequence',
              '!If sequence',
              '!Not sequence',
              '!Equals sequence',
              '!Or sequence',
              '!FindInMap sequence',
              '!Base64 scalar',
              '!Join sequence',
              '!Cidr sequence',
              '!Ref scalar',
              '!Sub scalar',
              '!Sub sequence',
              '!GetAtt scalar',
              '!GetAtt sequence',
              '!GetAZs mapping',
              '!GetAZs scalar',
              '!ImportValue mapping',
              '!ImportValue scalar',
              '!Select sequence',
              '!Split sequence',
            },
          },
        },
      },
    }

    -- Ensure the servers and tools above are installed
    --
    -- To check the current status of installed tools and/or manually install
    -- other tools, you can run
    --    :Mason
    --
    -- You can press `g?` for help in this menu.
    --
    -- `mason` had to be setup earlier: to configure its options see the
    -- `dependencies` table for `nvim-lspconfig` above.
    --
    -- You can add other tools here that you want Mason to install
    -- for you, so that they are available from within Neovim.
    local ensure_installed = vim.tbl_keys(servers or {})
    vim.list_extend(ensure_installed, {
      'actionlint',
      'basedpyright',
      'bash-language-server',
      'css-lsp',
      'delve',
      'deno',
      'docker_compose_language_service',
      'dockerfile-language-server',
      'eslint-lsp',
      'eslint',
      'graphql-language-service-cli',
      'hadolint',
      'html-lsp',
      'json-lsp',
      'jsonlint',
      'jsonnet-language-server',
      'jsonnetfmt',
      'lua-language-server',
      'markdownlint',
      'marksman',
      'prettier',
      'prettierd',
      'ruff',
      'rust-analyzer',
      'sonarlint-language-server',
      'stylua', -- Used to format Lua code
      'tailwindcss-language-server',
      'tflint',
      'yaml-language-server',
      'yamllint',
      'js-debug-adapter',
      'firefox-debug-adapter',
    })
    require('mason-tool-installer').setup({ ensure_installed = ensure_installed })

    -- FIXME: Look into moving this into typescript-tools.lua, particularly the keymap config
    require('mason-lspconfig').setup({
      handlers = {
        function(server_name)
          local server = servers[server_name] or {}
          -- This handles overriding only values explicitly passed
          -- by the server configuration above. Useful when disabling
          -- certain features of an LSP (for example, turning off formatting for ts_ls)
          server.capabilities = vim.tbl_deep_extend('force', {}, capabilities, server.capabilities or {})
          require('lspconfig')[server_name].setup(server)
        end,
        ['ts_ls'] = function()
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
            vim.keymap.set('n', 'gd', ':TSToolsGoToSourceDefinition<CR>', opts)
          end

          local function clear_keymaps()
            local keys = {
              '<leader>rf',
              '<leader>oi',
              '<leader>ru',
              '<leader>ai',
              '<leader>cf',
              '<leader>gfr',
              'gd',
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
      },
    })
  end,
}
