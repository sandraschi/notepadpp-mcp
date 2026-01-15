use zed_extension_api as zed;

struct NotepadTextEditingExtension;

impl zed::Extension for NotepadTextEditingExtension {
    fn context_server_command(
        &mut self,
        id: &zed::ContextServerId,
        _project: &zed::Project,
    ) -> zed::Result<zed::Command> {
        match id.0.as_str() {
            "notepadpp-mcp" => Ok(zed::Command {
                command: "uv".to_string(),
                args: vec!["run".to_string(), "notepadpp_mcp.tools.server:run".to_string()],
                env: Default::default(),
            }),
            _ => Err(format!("Unknown server: {}", id.0)),
        }
    }
}

zed::register_extension!(NotepadTextEditingExtension);
