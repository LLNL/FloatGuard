#pragma once

using namespace std;
using namespace clang;
using namespace llvm;

extern string g_mainFilename;
extern string g_dirName;
extern string g_pluginRoot;
extern Rewriter rewriter;

#define VARDECL_READ 1
#define VARDECL_WRITE 2
#define VARDECL_DECL 3

class InjectExceptionVisitor : public RecursiveASTVisitor<InjectExceptionVisitor> {
private:
    ASTContext *astContext;
    std::map<std::string, FileID> sourceFiles;    
public:
    explicit InjectExceptionVisitor(CompilerInstance *CI)
        : astContext(&(CI->getASTContext())) // initialize private members
    {
        rewriter.setSourceMgr(astContext->getSourceManager(),
            astContext->getLangOpts());     
    }
    virtual bool VisitFunctionDecl(FunctionDecl* func);
    virtual bool VisitStmt(Stmt* stmt);
    std::map<std::string, FileID>& getSourceFiles() { return sourceFiles; }
};

class TransformMutationsASTConsumer : public ASTConsumer {
private:
    CompilerInstance* compI;
    InjectExceptionVisitor *visitor; // doesn't have to be private

public:
    explicit TransformMutationsASTConsumer(CompilerInstance *CI)
        : compI(CI)
        , visitor(new InjectExceptionVisitor(CI)) // initialize the visitor
        { }
 
    virtual void HandleTranslationUnit(ASTContext &Context);
};

class PluginTransformMutationsAction : public PluginASTAction {
protected:
    unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI, StringRef file); 
    bool ParseArgs(const CompilerInstance &CI, const vector<string> &args);
};
