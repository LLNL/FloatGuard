#include <iostream>
#include <sstream>
#include <string>
#include <unistd.h>
#include <sys/stat.h>
#include <iomanip>

#include "utils.h"
#include "TransformMutations.h"

bool InjectExceptionVisitor::VisitFunctionDecl(FunctionDecl* func) {
    if (!func->doesThisDeclarationHaveABody()) {
        return true;
    }

    // check function signature (host/global/device) and determine the types to use for replacement
    bool isKernelFunc = false;
    SourceRange declRange = clang::SourceRange(func->getSourceRange().getBegin(), func->getBody()->getSourceRange().getBegin());
    StringRef declStr = Lexer::getSourceText(clang::CharSourceRange::getTokenRange(declRange), astContext->getSourceManager(), astContext->getLangOpts());
    if (declStr.find("__global__") != std::string::npos) {
        isKernelFunc = true;
    }

    if (isKernelFunc){
        const CompoundStmt *fBody = dyn_cast<CompoundStmt>(func->getBody());        
        SourceLocation startingPoint = astContext->getSourceManager().getFileLoc(fBody->body_front()->getBeginLoc());
        std::string fileName = astContext->getSourceManager().getFilename(startingPoint).str();
        FileID fileID = astContext->getSourceManager().getFileID(startingPoint);
        sourceFiles[fileName] = fileID;
        PrintSourceLocation(startingPoint, astContext);
        rewriter.InsertText(startingPoint, "ENABLE_FP_EXCEPTION(RANDINT);\n");
        return true;
    }
    else {
        return true;
    }
}

bool InjectExceptionVisitor::VisitStmt(Stmt* stmt) {
    SourceLocation startingPoint = astContext->getSourceManager().getFileLoc(stmt->getBeginLoc());
    std::string calleeName = ""; 
    if (isa<CUDAKernelCallExpr>(stmt)) {
        PRINT_DEBUG_MESSAGE( "has cuda kernel call:");
        PrintSourceRange(stmt->getSourceRange(), astContext);
        CUDAKernelCallExpr* call = dyn_cast<CUDAKernelCallExpr>(stmt);        
        if (call->getDirectCallee())
            calleeName = call->getDirectCallee()->getNameAsString();          
    }
    else if (isa<CallExpr>(stmt)) {
        CallExpr* call = dyn_cast<CallExpr>(stmt);
        if (call->getDirectCallee()) {
            calleeName = call->getDirectCallee()->getNameAsString();                  
            if (calleeName.find("hipLaunchkernel") != std::string::npos) {
                PRINT_DEBUG_MESSAGE( "has hip kernel call:");
            }
            else
                return true;            
        }
        else
            return true;
    }
    else
        return true;
    
    std::string fileName = astContext->getSourceManager().getFilename(startingPoint).str();
    FileID fileID = astContext->getSourceManager().getFileID(startingPoint);
    sourceFiles[fileName] = fileID;
    rewriter.InsertText(startingPoint, "set_fp_exception_enabled(\"__device_stub__" + calleeName + "()\");\n");

    return true;
}

void TransformMutationsASTConsumer::HandleTranslationUnit(ASTContext &Context) {
    clang::TargetOptions& targetOpts = compI->getTargetOpts();
    if (targetOpts.Triple.find("amdgcn") == std::string::npos)
        return;

    visitor->TraverseDecl(Context.getTranslationUnitDecl());

    map<std::string, FileID>::iterator it;
    map<std::string, FileID>& sourceFiles = visitor->getSourceFiles();
    // save original files (but with a marker)
    for (it = sourceFiles.begin(); it != sourceFiles.end(); it++)
    {
        // insert macro at the beginning of the file
        FileID id = it->second;
        string originalFilename = it->first;

        // check if file is already injected
        //std::ifstream t(originalFilename);
        //std::stringstream buffer;
        //buffer << t.rdbuf();
        //if (buffer.str().find("set_fp_exception_enabled(\"") != std::string::npos ||
        //    buffer.str().find("ENABLE_FP_EXCEPTION(RANDINT);") != std::string::npos) {
        //    continue;
        //}

        std::string bufferData = Context.getSourceManager().getBufferData(id).str();
        if (bufferData.find("set_fp_exception_enabled") != std::string::npos ||
            bufferData.find("ENABLE_FP_EXCEPTION") != std::string::npos) {
            continue;
        }

        // Create an output file to write the updated code
        std::error_code OutErrorInfo;
        std::error_code ok;
        const RewriteBuffer *RewriteBuf = rewriter.getRewriteBufferFor(id);
        if (RewriteBuf) {
            llvm::raw_fd_ostream outFile(llvm::StringRef(originalFilename),
                OutErrorInfo, llvm::sys::fs::OF_None);
            if (OutErrorInfo == ok) {
                outFile << std::string(RewriteBuf->begin(), RewriteBuf->end());
                PRINT_DEBUG_MESSAGE("Output file created - " << originalFilename);
            } else {
                PRINT_DEBUG_MESSAGE("Could not create file - " << originalFilename);
            }
        }
    }
}

unique_ptr<ASTConsumer> PluginTransformMutationsAction::CreateASTConsumer(CompilerInstance &CI, StringRef file) {
    PRINT_DEBUG_MESSAGE("Filename: " << file.str());

    g_mainFilename = file.str();
    g_dirName = basename(g_mainFilename);
    size_t dotpos = g_dirName.find(".");
    if (dotpos != std::string::npos)
        g_dirName = g_dirName.replace(dotpos, 1, "_");

    return make_unique<TransformMutationsASTConsumer>(&CI);
}
 
bool PluginTransformMutationsAction::ParseArgs(const CompilerInstance &CI, const vector<string> &args) {
    return true;
}