((nil . ((eval . (with-eval-after-load 'lsp-mode
                   (setq lsp-file-watch-ignored-directories
                         (cl-remove-duplicates
                          (append lsp-file-watch-ignored-directories
                                  ;; Python ignored directories
                                  '("[/\\\\]__pycache__\\'"
                                    "[/\\\\]\\.venv\\'"
                                    "[/\\\\]\\.eggs\\'"
                                    "[/\\\\]build\\'"
                                    "[/\\\\]model\\'"
                                    "[/\\\\]html_code_coverage\\'"
                                    "[/\\\\]\\.mypy_cache\\'"
                                    "[/\\\\]\\.tox\\'")

                                  ;; JS/TS ignored directories
                                  '("[/\\\\]node_modules\\'"
                                    "[/\\\\]out\\'"
                                    "[/\\\\].vscode\\'"
                                    "[/\\\\].vscode-test\\'"))))))
         (projectile-create-missing-test-files . t)))
 (python-mode . ((projectile-project-type . python-pkg)
                 (projectile-project-test-cmd . "cd python; flake8 . && nose2 -c tox.ini")
                 (python-backend . lsp)
                 (python-lsp-server . pyright)
                 (python-formatter . black)
                 (python-test-runner . nose)
                 (python-fill-column . 127)
                 (python-tab-width . 4)
                 (python-format-on-save . nil)
                 (python-sort-imports-on-save . nil)
                 (blacken-line-length . 'fill)))
 (typescript-mode . ((eval . (with-eval-after-load 'projectile
                               (projectile-register-project-type 'yarn '("package.json")
                                                                 :project-file "package.json"
                                                                 :compile "yarn compile"
                                                                 :src-dir "src/"
                                                                 :test "yarn test"
                                                                 :test-dir "src/test/suite/"
                                                                 :test-suffix ".test")))
                     (projectile-project-type . yarn)
                     (fill-column . 127))))