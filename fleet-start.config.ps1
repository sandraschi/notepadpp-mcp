# Per-repo fleet start config for notepadpp-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'notepadpp-mcp'
    BackendPort  = 10815
    FrontendPort = 10814
    HealthPath   = '/health'
    WebRoot      = 'D:\Dev\repos\notepadpp-mcp\web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'notepadpp_mcp.server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10815' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
