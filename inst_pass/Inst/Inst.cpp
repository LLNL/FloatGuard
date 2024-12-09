#include "llvm/Bitcode/BitcodeWriter.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Pass.h"
//#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Support/ToolOutputFile.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/Function.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/IR/DebugInfoMetadata.h"

#include <iostream>
#include <sstream>
#include <memory>
#include <string>
#include <cxxabi.h>
using namespace llvm;
using namespace llvm::legacy;

#define DEBUG_PRINT 0

#if LLVM_VERSION_MAJOR >= 15
#define GET_PTR_TY builder.getPtrTy()
#else
#define GET_PTR_TY Type::getInt8PtrTy(module->getContext())
#endif

namespace {

  inline std::string demangle(const char* name) 
  {
          int status = -1; 

          std::unique_ptr<char, void(*)(void*)> res { abi::__cxa_demangle(name, NULL, NULL, &status), std::free };
          return (status == 0) ? res.get() : std::string(name);
  }

  StringRef getFunctionName(CallInst *call) {
    Function *fun = call->getCalledFunction();
    if (fun)
      return fun->getName();
    else
      return StringRef("indirect call");
  }

  std::map<std::string, std::string> mangledFuncNames;
  std::string enableFpExceptionFuncName = "";

  void injectFPProfileCall(Instruction& I, BasicBlock& BB, IRBuilder<>& builder, Module* module) {
    builder.SetInsertPoint(&I);
    // Declare C standard library printf 
    Type *intType = Type::getInt32Ty(module->getContext());
    std::vector<Type *> printfArgsTypes({GET_PTR_TY});
    FunctionType *printfType = FunctionType::get(intType, printfArgsTypes, true);
    FunctionCallee printfFunc = module->getOrInsertFunction("printf", printfType);
    std::string printStr = "ins ";
    printStr += I.getOpcodeName();
    printStr += "\n";
    Value *str = builder.CreateGlobalStringPtr(printStr.c_str(), printStr.c_str());
    std::vector<Value *> argsV({str});
    builder.CreateCall(printfFunc, argsV, "calltmp");
  }

  bool processOthers(Function &F, Module* module, IRBuilder<>& builder);

  bool processMain(Function &F, Module* module, IRBuilder<>& builder) {
    Function::iterator FI = F.begin();
    BasicBlock &BB = *FI;
    BasicBlock::iterator BBI = BB.begin();
    Instruction &I = *BBI;

    builder.SetInsertPoint(&I);
    // Declare C standard library printf 
    Type *intType = Type::getInt32Ty(module->getContext());
    std::vector<Type *> printfArgsTypes({GET_PTR_TY});
    FunctionType *printfType = FunctionType::get(intType, printfArgsTypes, true);
    FunctionCallee printfFunc = module->getOrInsertFunction("init_fp_exception_sequence", printfType);
    std::vector<Value *> argsV;
    builder.CreateCall(printfFunc, argsV, "calltmp");    

    processOthers(F, module, builder);

    return false;
  }

  bool processKernel(Function &F, Module* module, IRBuilder<>& builder) {
    Function::iterator FI = F.begin();
    BasicBlock &BB = *FI;
    BasicBlock::iterator BBI = BB.begin();
    Instruction &I = *BBI;

    std::string func_name = demangle(F.getName().str().c_str());

    builder.SetInsertPoint(&I);
    // Declare C standard library printf 
    Type *intType = Type::getVoidTy(module->getContext());
    std::vector<Type *> printfArgsTypes({GET_PTR_TY});
    FunctionType *printfType = FunctionType::get(intType, printfArgsTypes, false);
    FunctionCallee printfFunc = module->getOrInsertFunction(enableFpExceptionFuncName, printfType);
    std::vector<Value *> argsV;
    builder.CreateCall(printfFunc, argsV, "calltmp");    
    return false;    
  }

  bool processOthers(Function &F, Module* module, IRBuilder<>& builder) {
    for (BasicBlock &BB : F) {
      #if DEBUG_PRINT
      errs() << "Basic block (name=" << BB.getName() << ") has "
                << BB.size() << " instructions.\n";
      #endif
      int insIndex = 0;
      for (Instruction &I : BB) {
        #if DEBUG_PRINT
        errs() << "Instruction " << insIndex << ":" << I << "\n";
        #endif
        if (I.getOpcode() == Instruction::PHI)
          continue;
        bool hasFloat = false;
        if (CallInst *callI = dyn_cast<CallInst>(&I)) {
          if (getFunctionName(callI).str() == "hipLaunchKernel") {
            errs() << "call: " << getFunctionName(callI) << "\n";

            builder.SetInsertPoint(&I);
            // Declare C standard library printf 
            Type *intType = Type::getVoidTy(module->getContext());
            std::vector<Type *> printfArgsTypes({GET_PTR_TY});
            FunctionType *printfType = FunctionType::get(intType, printfArgsTypes, false);
            FunctionCallee printfFunc = module->getOrInsertFunction(mangledFuncNames["set_fp_exception_enabled(char*)"], printfType);
            std::string printStr = demangle(F.getName().str().c_str());
            Value *str = builder.CreateGlobalStringPtr(printStr.c_str(), printStr.c_str());
            std::vector<Value *> argsV({str});
            builder.CreateCall(printfFunc, argsV, "calltmp");               
          }
        }
        insIndex++;
      }
    }    

    return false;
  }

  bool instFunction(Function &F) {
    Module* module = F.getParent();
    IRBuilder<> builder(module->getContext());

    std::string func_name = demangle(F.getName().str().c_str());

    errs() << "function name:" << func_name << " type: " << (int)F.getCallingConv() << "\n";
    mangledFuncNames[func_name] = F.getName().str();

    if (func_name == "main") {
      processMain(F, module, builder);
    }
    else if (func_name.find("setfpexception") != std::string::npos) {
      errs() << "found exception kernel func\n";
      enableFpExceptionFuncName = func_name;
    }
    else if (F.getCallingConv() == llvm::CallingConv::AMDGPU_KERNEL) {
      processKernel(F, module, builder);
    }
    else {
      processOthers(F, module, builder);
    }

    return false;    
  }

  struct InstPass : public FunctionPass {
    static char ID;
    InstPass() : FunctionPass(ID) {}

    virtual bool runOnFunction(Function &F) {
		  return instFunction(F);
    }

    virtual bool doFinalization(Module& M) {
      return false;
    }
  };

  struct Inst : public PassInfoMixin<Inst> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &) {
      if (!instFunction(F))
        return PreservedAnalyses::all();
      return PreservedAnalyses::none();
    }
  
    static bool isRequired() {
      return true;
    }
  };
}

PassPluginLibraryInfo getInstPassPluginInfo() {
  const auto callback = [](PassBuilder &PB) {
    PB.registerPipelineStartEPCallback (
        [&](ModulePassManager &MPM, OptimizationLevel opt) {
		      errs() << "opt:" << opt.getSpeedupLevel() << "\n";
          MPM.addPass(createModuleToFunctionPassAdaptor(Inst()));
        });
  };

  return {LLVM_PLUGIN_API_VERSION, "name", "0.0.1", callback};
};

extern "C" LLVM_ATTRIBUTE_WEAK PassPluginLibraryInfo llvmGetPassPluginInfo() {
  return getInstPassPluginInfo();
}