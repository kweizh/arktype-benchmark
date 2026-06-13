import { configure } from "arktype/config";

// Must be imported BEFORE arktype (and any module that imports arktype)
// so that $ark.config is set before kinds.js freezes resolvedConfig and
// before any type is parsed/compiled with applyConfig.
configure({ numberAllowsNaN: true });
