#include "utils.h"
#include "TransformMutations.h"

Rewriter rewriter;
string g_mainFilename;
string g_dirName;
string g_pluginRoot;
bool g_limitedMode = false;

FrontendPluginRegistry::Add<PluginTransformMutationsAction>
    TransformMutationsAction("inject-fp-exception", "inject excpetion enabling code");